import os
import tempfile
import unittest
import json
import time

from core.registry import SkillRegistry
from core.cache import SmartCache
from core.search import SearchEngine
from core.router import TaskRouter
from core.validator import SkillValidator
from nexora.cli import main as cli_main
from scripts.verify_no_comments import audit_repository

def create_sample_skill(skill_id="nexora.binary.disassembly.sweep", category="binary_analysis_and_reverse_engineering"):
    return {
        "id": skill_id,
        "name": "Linear Sweep Disassembler",
        "purpose": "Disassembles raw binary buffers into linear instruction sequences",
        "category": category,
        "subcategory": "disassembly_and_control_flow",
        "description": "Performs linear sweep decoding of instructions across binary executable sections with architectural validation.",
        "supported_platforms": ["windows", "linux", "ida_pro"],
        "activation_conditions": {
            "intent_patterns": ["disassemble binary buffer", "decode machine code"],
            "prerequisites": ["binary buffer loaded in memory"]
        },
        "required_inputs": [
            {
                "name": "binary_buffer",
                "type": "buffer",
                "description": "Target raw executable byte stream",
                "required": True
            }
        ],
        "expected_outputs": [
            {
                "name": "instruction_list",
                "type": "array",
                "description": "Sequential decoded assembly instructions"
            }
        ],
        "execution_workflow": [
            {
                "step_number": 1,
                "action": "Validate machine architecture and binary headers",
                "description": "Inspect header format and target bitness",
                "expected_outcome": "Valid architecture descriptor confirmed"
            }
        ],
        "decision_logic": {
            "rules": [
                {
                    "condition": "Invalid byte sequence encountered",
                    "action": "Mark undefined instruction and advance program counter"
                }
            ],
            "fallback": "Abort sweep and switch to recursive descent"
        },
        "tool_requirements": [
            {
                "tool_name": "disassemble_function",
                "server_name": "ida-pro",
                "optional": True
            }
        ],
        "dependencies": {
            "system_libraries": ["libcapstone"],
            "runtime_packages": ["capstone"],
            "skill_dependencies": []
        },
        "safety_restrictions": [
            "Do not execute unverified binary buffers in host process"
        ],
        "validation_criteria": [
            "Disassembly output matches instruction stream specifications"
        ],
        "practical_examples": [
            {
                "scenario": "Decode PE .text section entrypoint",
                "input": {"binary_buffer": "4883ec28"},
                "expected_output": {"instruction_list": ["sub rsp, 0x28"]}
            }
        ],
        "related_skills": ["nexora.binary.cfg.builder"],
        "version": "1.0.0"
    }

class TestSkillRegistry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_registry.db")
        self.registry = SkillRegistry(db_path=self.db_path)

    def tearDown(self):
        self.registry.close()
        self.temp_dir.cleanup()

    def test_insert_and_get_skill(self):
        skill = create_sample_skill()
        inserted = self.registry.insert_skill(skill)
        self.assertTrue(inserted)

        retrieved = self.registry.get_skill_by_id(skill["id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["id"], skill["id"])
        self.assertEqual(retrieved["name"], skill["name"])

    def test_count_and_delete_skill(self):
        self.assertEqual(self.registry.count_skills(), 0)
        skill = create_sample_skill()
        self.registry.insert_skill(skill)
        self.assertEqual(self.registry.count_skills(), 1)

        deleted = self.registry.delete_skill(skill["id"])
        self.assertTrue(deleted)
        self.assertEqual(self.registry.count_skills(), 0)
        self.assertIsNone(self.registry.get_skill_by_id(skill["id"]))

    def test_fts5_search(self):
        skill1 = create_sample_skill("nexora.binary.sweep", "binary_analysis_and_reverse_engineering")
        skill2 = create_sample_skill("nexora.software.synthesis", "software_engineering_and_architecture")
        skill2["name"] = "Python AST Rewriter"
        skill2["purpose"] = "Synthesizes and rewrites abstract syntax trees cleanly"
        skill2["description"] = "Refactors Python abstract syntax trees with automated code transforms."

        self.registry.insert_skill(skill1)
        self.registry.insert_skill(skill2)

        results = self.registry.search_skills("sweep")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "nexora.binary.sweep")

        ast_results = self.registry.search_skills("abstract syntax trees")
        self.assertEqual(len(ast_results), 1)
        self.assertEqual(ast_results[0]["id"], "nexora.software.synthesis")

    def test_list_and_filter_categories(self):
        skill1 = create_sample_skill("nexora.skill1", "binary_analysis_and_reverse_engineering")
        skill2 = create_sample_skill("nexora.skill2", "software_engineering_and_architecture")
        self.registry.insert_skill(skill1)
        self.registry.insert_skill(skill2)

        categories = self.registry.list_categories()
        self.assertIn("binary_analysis_and_reverse_engineering", categories)
        self.assertIn("software_engineering_and_architecture", categories)

        binary_skills = self.registry.get_skills_by_category("binary_analysis_and_reverse_engineering")
        self.assertEqual(len(binary_skills), 1)
        self.assertEqual(binary_skills[0]["id"], "nexora.skill1")

    def test_export_index(self):
        skill = create_sample_skill()
        self.registry.insert_skill(skill)

        export_path = os.path.join(self.temp_dir.name, "index.json")
        count = self.registry.export_index(export_path)
        self.assertEqual(count, 1)
        self.assertTrue(os.path.exists(export_path))

        with open(export_path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        self.assertEqual(data["total_skills"], 1)
        self.assertEqual(len(data["skills"]), 1)

class TestSmartCache(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = os.path.join(self.temp_dir.name, "cache")
        self.cache = SmartCache(cache_dir=self.cache_dir, max_memory_items=2)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_set_and_get_memory_and_disk(self):
        val = {"payload": "sample_data"}
        cache_key = "test_key_1"
        content_hash = self.cache.set(cache_key, val)

        self.assertIsInstance(content_hash, str)
        self.assertEqual(len(content_hash), 64)

        retrieved = self.cache.get(cache_key)
        self.assertEqual(retrieved, val)
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 0)

    def test_lru_memory_eviction(self):
        self.cache.set("key1", "val1")
        self.cache.set("key2", "val2")
        self.cache.set("key3", "val3")

        self.assertNotIn("key1", self.cache.memory_cache)
        self.assertIn("key2", self.cache.memory_cache)
        self.assertIn("key3", self.cache.memory_cache)

        val1 = self.cache.get("key1")
        self.assertEqual(val1, "val1")
        self.assertIn("key1", self.cache.memory_cache)

    def test_file_modification_invalidation(self):
        test_file = os.path.join(self.temp_dir.name, "source.txt")
        with open(test_file, "w", encoding="utf-8") as file_handle:
            file_handle.write("initial content")

        self.cache.set_by_file(test_file, {"data": "cached_version"})
        self.assertEqual(self.cache.get_by_file(test_file), {"data": "cached_version"})

        time.sleep(0.05)
        with open(test_file, "w", encoding="utf-8") as file_handle:
            file_handle.write("modified content")

        result_after_mod = self.cache.get_by_file(test_file)
        self.assertIsNone(result_after_mod)

    def test_clear_and_inspect(self):
        self.cache.set("keyA", "valA")
        self.cache.set("keyB", "valB")

        inspect_results = self.cache.inspect()
        self.assertEqual(len(inspect_results), 2)

        self.cache.clear()
        stats = self.cache.get_stats()
        self.assertEqual(stats["memory_entries"], 0)
        self.assertEqual(stats["disk_entries"], 0)

class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "search_test.db")
        self.registry = SkillRegistry(db_path=self.db_path)
        self.engine = SearchEngine(registry=self.registry)

        skill1 = create_sample_skill("nexora.skill.disassemble", "binary_analysis_and_reverse_engineering")
        skill2 = create_sample_skill("nexora.skill.game", "game_development_and_virtual_worlds")
        skill2["name"] = "Roblox Luau Character Controller"
        skill2["purpose"] = "Controls avatar kinematics and physics simulation in Roblox Studio"
        skill2["subcategory"] = "gameplay_mechanics"
        skill2["supported_platforms"] = ["roblox_studio"]
        skill2["tool_requirements"] = [{"tool_name": "execute_luau", "server_name": "Roblox_Studio", "optional": False}]

        self.registry.insert_skill(skill1)
        self.registry.insert_skill(skill2)

    def tearDown(self):
        self.registry.close()
        self.temp_dir.cleanup()

    def test_search_with_platform_filter(self):
        roblox_results = self.engine.search(platform="roblox_studio")
        self.assertEqual(len(roblox_results), 1)
        self.assertEqual(roblox_results[0]["id"], "nexora.skill.game")

        windows_results = self.engine.search(platform="windows")
        self.assertEqual(len(windows_results), 1)
        self.assertEqual(windows_results[0]["id"], "nexora.skill.disassemble")

    def test_match_capabilities(self):
        matched = self.engine.match_capabilities(required_tools=["execute_luau"])
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["id"], "nexora.skill.game")

    def test_suggest_skills(self):
        suggestions = self.engine.suggest_skills("disassemble", limit=5)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["id"], "nexora.skill.disassemble")

class TestTaskRouter(unittest.TestCase):
    def setUp(self):
        self.router = TaskRouter()

    def test_complexity_simple(self):
        analysis = self.router.analyze_complexity("Disassemble a small function")
        self.assertEqual(analysis["complexity"], "SIMPLE")

    def test_complexity_large(self):
        analysis = self.router.analyze_complexity("Execute batch generator for 3000 skills across entire repository")
        self.assertEqual(analysis["complexity"], "LARGE")

    def test_detect_domain(self):
        domain = self.router.detect_domain("Analyze android apk using adb and frida hook")
        self.assertEqual(domain, "mobile_security_and_app_analysis")

        roblox_domain = self.router.detect_domain("Build a Roblox Luau avatar physics controller in studio")
        self.assertEqual(roblox_domain, "game_development_and_virtual_worlds")

    def test_route_task(self):
        decision = self.router.route_task("Disassemble PE binary header with ida pro")
        self.assertEqual(decision["detected_domain"], "binary_analysis_and_reverse_engineering")
        self.assertEqual(decision["primary_agent"], "binary_reverse_engineering_agent")
        self.assertIn("workflow_steps", decision)

class TestSkillValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SkillValidator()

    def test_validate_valid_skill(self):
        skill = create_sample_skill()
        is_valid, errors = self.validator.validate_skill(skill)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_invalid_skill(self):
        invalid_skill = {"id": "invalid"}
        is_valid, errors = self.validator.validate_skill(invalid_skill)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "cli_test.db")
        self.cache_dir = os.path.join(self.temp_dir.name, "cli_cache")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_init_and_stats(self):
        init_code = cli_main(["init", "--db", self.db_path, "--cache-dir", self.cache_dir])
        self.assertEqual(init_code, 0)
        self.assertTrue(os.path.exists(self.db_path))

        stats_code = cli_main(["stats", "--db", self.db_path, "--cache-dir", self.cache_dir, "--json"])
        self.assertEqual(stats_code, 0)

    def test_cli_validate(self):
        skill = create_sample_skill()
        skill_file = os.path.join(self.temp_dir.name, "skill.json")
        with open(skill_file, "w", encoding="utf-8") as file_handle:
            json.dump(skill, file_handle)

        val_code = cli_main(["validate", skill_file, "--json"])
        self.assertEqual(val_code, 0)

class TestVerifyNoComments(unittest.TestCase):
    def test_repository_zero_comments(self):
        report = audit_repository(".")
        self.assertEqual(report["total_violations"], 0)

if __name__ == "__main__":
    unittest.main()
