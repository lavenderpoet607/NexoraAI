import os
import sys

sys.path.insert(0, os.path.abspath("."))

import json
from core.registry import SkillRegistry
from core.exporter import PlatformExporter

def main() -> int:
    registry = SkillRegistry()
    total_skills = registry.count_skills()
    print(f"Reading {total_skills} skills for platform packaging...")

    index_path = "registry/skill_index.json"
    if not os.path.exists(index_path):
        registry.export_index(index_path)

    with open(index_path, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    skills = data.get("skills", [])
    registry.close()

    exporter = PlatformExporter(output_root="platforms")

    print(f"Exporting skills across 11 target platforms...")
    summary = exporter.export_all(skills[:100], base_dir="platforms")

    for platform_name, exported_files in summary.items():
        print(f"  - {platform_name}: {len(exported_files)} files generated")

    print("Platform export completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

