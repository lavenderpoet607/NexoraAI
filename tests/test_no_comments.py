import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))

from scripts.verify_no_comments import audit_repository

class TestNoCommentsPolicy(unittest.TestCase):
    def test_repository_contains_strictly_zero_comments(self):
        report = audit_repository(".")
        total_violations = report.get("total_violations", 0)
        violations_dict = report.get("violations", {})
        if total_violations > 0:
            error_lines = []
            for file_path, items in list(violations_dict.items())[:20]:
                for item in items:
                    error_lines.append(f"{file_path}:{item[0]} - {item[1]}")
            self.fail(f"Found {total_violations} comment violations in {len(violations_dict)} files:\n" + "\n".join(error_lines))
        self.assertEqual(total_violations, 0)
        self.assertGreater(report.get("scanned_files", 0), 3000)

if __name__ == "__main__":
    unittest.main()
