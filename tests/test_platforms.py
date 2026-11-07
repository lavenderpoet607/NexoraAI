import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.abspath("."))

from core.registry import SkillRegistry
from core.exporter import PlatformExporter

class TestPlatformAdapters(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.registry = SkillRegistry()
        self.skills = self.registry.search_skills("", limit=10)
        self.exporter = PlatformExporter(output_root=self.temp_dir)

    def tearDown(self):
        self.registry.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_antigravity(self):
        target = os.path.join(self.temp_dir, "antigravity")
        files = self.exporter.export_antigravity(self.skills, target)
        self.assertEqual(len(files), len(self.skills))
        for f in files:
            self.assertTrue(os.path.exists(f))
            self.assertTrue(f.endswith("SKILL.md"))

    def test_export_claude_code(self):
        target = os.path.join(self.temp_dir, "claude")
        files = self.exporter.export_claude_code(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(os.path.exists(files[0]))
        self.assertTrue(files[0].endswith("CLAUDE.md"))

    def test_export_cursor(self):
        target = os.path.join(self.temp_dir, "cursor")
        files = self.exporter.export_cursor(self.skills, target)
        self.assertEqual(len(files), len(self.skills))
        for f in files:
            self.assertTrue(f.endswith(".mdc"))

    def test_export_windsurf(self):
        target = os.path.join(self.temp_dir, "windsurf")
        files = self.exporter.export_windsurf(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith(".windsurfrules"))

    def test_export_copilot(self):
        target = os.path.join(self.temp_dir, "copilot")
        files = self.exporter.export_copilot(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("copilot-instructions.md"))

    def test_export_cline(self):
        target = os.path.join(self.temp_dir, "cline")
        files = self.exporter.export_cline(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith(".clinerules"))

    def test_export_roo_code(self):
        target = os.path.join(self.temp_dir, "roo")
        files = self.exporter.export_roo_code(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith(".roomodes"))

    def test_export_gemini_cli(self):
        target = os.path.join(self.temp_dir, "gemini")
        files = self.exporter.export_gemini_cli(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("GEMINI.md"))

    def test_export_codex(self):
        target = os.path.join(self.temp_dir, "codex")
        files = self.exporter.export_codex(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("codex_prompt.md"))

    def test_export_continue(self):
        target = os.path.join(self.temp_dir, "continue")
        files = self.exporter.export_continue(self.skills, target)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith("config.json"))

    def test_export_aider(self):
        target = os.path.join(self.temp_dir, "aider")
        files = self.exporter.export_aider(self.skills, target)
        self.assertEqual(len(files), 2)

    def test_export_all_platforms(self):
        summary = self.exporter.export_all(self.skills[:5], self.temp_dir)
        self.assertEqual(len(summary), 11)

if __name__ == "__main__":
    unittest.main()

