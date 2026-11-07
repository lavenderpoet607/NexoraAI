import sys
import os
import json
import argparse
from typing import Optional, List

from core.registry import SkillRegistry
from core.cache import SmartCache
from core.search import SearchEngine
from core.validator import SkillValidator

def handle_init(args: argparse.Namespace) -> int:
    os.makedirs("registry", exist_ok=True)
    os.makedirs(args.cache_dir, exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)

    registry = SkillRegistry(db_path=args.db)
    registry.close()

    result = {
        "status": "success",
        "message": "Nexora AI ecosystem directories and registry database initialized",
        "database": args.db,
        "cache_dir": args.cache_dir
    }
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))
    else:
        print(result["message"])
        print(f"Database: {result['database']}")
        print(f"Cache: {result['cache_dir']}")
    return 0

def handle_search(args: argparse.Namespace) -> int:
    query = args.query or ""
    registry = SkillRegistry(db_path=args.db)
    engine = SearchEngine(registry=registry)

    results = engine.search(
        query=query,
        category=args.category,
        platform=args.platform,
        limit=args.limit
    )
    registry.close()

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"Found {len(results)} matching skills:")
        for idx, skill in enumerate(results, start=1):
            platforms = ", ".join(skill.get("supported_platforms", []))
            print(f"[{idx}] {skill.get('id')} - {skill.get('name')}")
            print(f"    Category: {skill.get('category')} / {skill.get('subcategory')}")
            print(f"    Platforms: {platforms}")
            print(f"    Purpose: {skill.get('purpose')}")
    return 0

def handle_info(args: argparse.Namespace) -> int:
    registry = SkillRegistry(db_path=args.db)
    skill = registry.get_skill_by_id(args.skill_id)
    registry.close()

    if skill is None:
        if getattr(args, "json", False):
            print(json.dumps({"error": f"Skill not found: {args.skill_id}"}))
        else:
            print(f"Skill not found: {args.skill_id}")
        return 1

    if getattr(args, "json", False):
        print(json.dumps(skill, indent=2, ensure_ascii=False))
    else:
        print(f"Skill ID: {skill.get('id')}")
        print(f"Name: {skill.get('name')}")
        print(f"Version: {skill.get('version')}")
        print(f"Category: {skill.get('category')}")
        print(f"Subcategory: {skill.get('subcategory')}")
        print(f"Purpose: {skill.get('purpose')}")
        print(f"Supported Platforms: {', '.join(skill.get('supported_platforms', []))}")
        print("Description:")
        print(skill.get("description", ""))
        tools = skill.get("tool_requirements", [])
        if tools:
            print("Required Tools:")
            for tool in tools:
                server = f" ({tool.get('server_name')})" if tool.get("server_name") else ""
                print(f"  - {tool.get('tool_name')}{server}")
    return 0

def handle_validate(args: argparse.Namespace) -> int:
    validator = SkillValidator(schema_path=args.schema)
    target_path = args.path

    if os.path.isdir(target_path):
        report = validator.validate_directory(target_path)
    else:
        is_valid, errors = validator.validate_file(target_path)
        report = {
            "total": 1,
            "valid": 1 if is_valid else 0,
            "invalid": 0 if is_valid else 1,
            "errors": {target_path: errors} if not is_valid else {}
        }

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        print(f"Validation Summary: {report['valid']}/{report['total']} valid")
        if report["invalid"] > 0:
            print(f"Failed validations: {report['invalid']}")
            for file_path, errors in report["errors"].items():
                print(f"File: {file_path}")
                for err in errors:
                    print(f"  - {err}")

    return 0 if report["invalid"] == 0 else 1

def handle_export(args: argparse.Namespace) -> int:
    registry = SkillRegistry(db_path=args.db)

    if args.category:
        skills = registry.get_skills_by_category(args.category)
    elif args.platform:
        skills = registry.get_skills_by_platform(args.platform)
    else:
        skills = registry.list_skills()

    registry.close()

    output_path = args.output
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    payload = {
        "total_skills": len(skills),
        "skills": skills
    }
    with open(output_path, "w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=False)

    if getattr(args, "json", False):
        print(json.dumps({"status": "success", "exported_count": len(skills), "output_path": output_path}))
    else:
        print(f"Successfully exported {len(skills)} skills to {output_path}")
    return 0

def handle_stats(args: argparse.Namespace) -> int:
    registry = SkillRegistry(db_path=args.db)
    cache = SmartCache(cache_dir=args.cache_dir)

    total_skills = registry.count_skills()
    categories = registry.list_categories()
    category_breakdown = {}
    for cat in categories:
        category_breakdown[cat] = len(registry.get_skills_by_category(cat))

    registry.close()
    cache_stats = cache.get_stats()

    stats_data = {
        "total_skills": total_skills,
        "categories_count": len(categories),
        "category_breakdown": category_breakdown,
        "cache": cache_stats
    }

    if getattr(args, "json", False):
        print(json.dumps(stats_data, indent=2))
    else:
        print("=== Nexora AI Ecosystem Statistics ===")
        print(f"Total Skills: {total_skills}")
        print(f"Categories: {len(categories)}")
        for cat, count in category_breakdown.items():
            print(f"  - {cat}: {count}")
        print("Cache Statistics:")
        print(f"  - Hits: {cache_stats['hits']}, Misses: {cache_stats['misses']}")
        print(f"  - Hit Ratio: {cache_stats['hit_ratio']}")
        print(f"  - Memory Entries: {cache_stats['memory_entries']}, Disk Entries: {cache_stats['disk_entries']}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexora",
        description="Nexora AI Universal Skill Ecosystem CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--db", default="registry/nexora_registry.db")
    init_parser.add_argument("--cache-dir", default="cache")
    init_parser.add_argument("--json", action="store_true")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", nargs="?", default="", type=str)
    search_parser.add_argument("-c", "--category", type=str, default=None)
    search_parser.add_argument("-p", "--platform", type=str, default=None)
    search_parser.add_argument("-l", "--limit", type=int, default=20)
    search_parser.add_argument("--db", default="registry/nexora_registry.db")
    search_parser.add_argument("--json", action="store_true")

    info_parser = subparsers.add_parser("info")
    info_parser.add_argument("skill_id", type=str)
    info_parser.add_argument("--db", default="registry/nexora_registry.db")
    info_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=str)
    validate_parser.add_argument("--schema", type=str, default=None)
    validate_parser.add_argument("--json", action="store_true")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("-o", "--output", default="registry/skill_index.json")
    export_parser.add_argument("-c", "--category", type=str, default=None)
    export_parser.add_argument("-p", "--platform", type=str, default=None)
    export_parser.add_argument("--db", default="registry/nexora_registry.db")
    export_parser.add_argument("--json", action="store_true")

    stats_parser = subparsers.add_parser("stats")
    stats_parser.add_argument("--db", default="registry/nexora_registry.db")
    stats_parser.add_argument("--cache-dir", default="cache")
    stats_parser.add_argument("--json", action="store_true")

    return parser

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    command_handlers = {
        "init": handle_init,
        "search": handle_search,
        "info": handle_info,
        "validate": handle_validate,
        "export": handle_export,
        "stats": handle_stats
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    return 1

if __name__ == "__main__":
    sys.exit(main())
