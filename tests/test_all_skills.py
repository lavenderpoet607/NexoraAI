import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath("."))

from core.registry import SkillRegistry
from core.validator import SkillValidator

class TestAllSkillsEcosystem(unittest.TestCase):
    def setUp(self):
        self.registry = SkillRegistry()
        self.validator = SkillValidator()

    def tearDown(self):
        self.registry.close()

    def test_total_skill_count(self):
        total = self.registry.count_skills()
        self.assertEqual(total, 3000)

    def test_unique_skill_ids(self):
        index_path = "registry/skill_index.json"
        self.assertTrue(os.path.exists(index_path))
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.get("skills", [])
        self.assertEqual(len(skills), 3000)

        ids = [s["id"] for s in skills]
        names = [s["name"] for s in skills]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_taxonomy_category_distribution(self):
        with open("categories/taxonomy_matrix.json", "r", encoding="utf-8") as f:
            taxonomy = json.load(f)

        for category in taxonomy["categories"]:
            cat_id = category["id"]
            expected_quota = category["target_allocation"]
            actual_skills = self.registry.get_skills_by_category(cat_id)
            self.assertEqual(
                len(actual_skills),
                expected_quota,
                f"Mismatch in category {cat_id}: expected {expected_quota}, got {len(actual_skills)}"
            )

    def test_skill_schema_validity_sample(self):
        index_path = "registry/skill_index.json"
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.get("skills", [])

        stride = len(skills) // 30
        for i in range(0, len(skills), stride):
            skill = skills[i]
            is_valid, errors = self.validator.validate_skill(skill)
            self.assertTrue(is_valid, f"Validation failure for {skill.get('id')}: {errors}")

    def test_all_skills_have_mandatory_fields(self):
        index_path = "registry/skill_index.json"
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.get("skills", [])

        required_fields = [
            "id", "name", "purpose", "category", "subcategory",
            "description", "supported_platforms", "activation_conditions",
            "required_inputs", "expected_outputs", "execution_workflow",
            "decision_logic", "tool_requirements", "dependencies",
            "safety_restrictions", "validation_criteria", "practical_examples",
            "related_skills", "version"
        ]

        for s in skills:
            for field in required_fields:
                self.assertIn(field, s, f"Field {field} missing in {s.get('id')}")

if __name__ == "__main__":
    unittest.main()

