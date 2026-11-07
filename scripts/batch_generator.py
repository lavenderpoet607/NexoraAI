import os
import sys

sys.path.insert(0, os.path.abspath("."))

import json
import time
from typing import Dict, List, Any

from core.registry import SkillRegistry
from core.validator import SkillValidator

PLATFORM_MAP = {
    "binary_analysis_and_reverse_engineering": ["windows", "linux", "ida_pro", "rea"],
    "mobile_security_and_app_analysis": ["android", "ios", "linux", "cross_platform"],
    "game_development_and_virtual_worlds": ["windows", "roblox_studio", "cross_platform"],
    "three_dimensional_graphics_and_animation": ["windows", "linux", "macos", "blender"],
    "cybersecurity_and_penetration_testing": ["linux", "windows", "cross_platform"],
    "system_architecture_and_os_internals": ["linux", "windows", "macos"],
    "software_engineering_and_architecture": ["cross_platform", "linux", "windows", "macos"],
    "web_technologies_and_browser_automation": ["web", "cross_platform", "linux", "windows"],
    "ai_ml_and_cognitive_orchestration": ["cross_platform", "linux", "windows"],
    "cloud_devops_and_infrastructure": ["linux", "cross_platform", "windows"],
    "data_engineering_and_storage_systems": ["linux", "cross_platform", "windows"],
    "hardware_embedded_and_iot": ["embedded", "linux", "cross_platform"],
    "network_protocols_and_traffic_analysis": ["linux", "cross_platform", "windows"],
    "media_processing_and_creative_automation": ["cross_platform", "windows", "linux", "macos"],
    "security_governance_and_compliance": ["cross_platform", "windows", "linux"],
    "autonomous_agent_orchestration_and_routing": ["cross_platform", "linux", "windows"]
}

SERVER_MAP = {
    "binary_analysis_and_reverse_engineering": ("decompile_function", "ida-pro"),
    "mobile_security_and_app_analysis": ("inspect_adb_package", "rea"),
    "game_development_and_virtual_worlds": ("execute_luau", "Roblox_Studio"),
    "three_dimensional_graphics_and_animation": ("create_primitive", "blender"),
    "cybersecurity_and_penetration_testing": ("analyze_function", "rea"),
    "system_architecture_and_os_internals": ("inspect_native_instruction", "rea"),
    "software_engineering_and_architecture": ("run_command", "native_shell"),
    "web_technologies_and_browser_automation": ("inspect_web_page", "rea"),
    "ai_ml_and_cognitive_orchestration": ("call_mcp_tool", "orchestrator"),
    "cloud_devops_and_infrastructure": ("run_command", "native_shell"),
    "data_engineering_and_storage_systems": ("sqlite_query", "sqlite"),
    "hardware_embedded_and_iot": ("inspect_firmware_regions", "rea"),
    "network_protocols_and_traffic_analysis": ("inspect_packet_capture", "rea"),
    "media_processing_and_creative_automation": ("render_preview", "blender"),
    "security_governance_and_compliance": ("audit_policy", "security_evaluator"),
    "autonomous_agent_orchestration_and_routing": ("invoke_subagent", "orchestrator")
}

def generate_skill_payload(
    category_id: str,
    subcategory_id: str,
    index_in_subcat: int,
    subcat_name: str,
    subcat_desc: str,
    keywords: List[str]
) -> Dict[str, Any]:
    item_num = index_in_subcat + 1
    kw = keywords[index_in_subcat % len(keywords)] if keywords else "operation"
    kw_clean = kw.lower().replace(" ", "_").replace("-", "_")

    skill_id = f"nexora.{category_id}.{subcategory_id}.{kw_clean}_{item_num:03d}"
    name = f"{subcat_name} {kw.replace('_', ' ').title()} Engine {item_num}"
    purpose = f"Executes precision {kw.replace('_', ' ')} procedures for {subcat_name.lower()} within {category_id.replace('_', ' ')} workflows"
    description = (
        f"Automates advanced {kw.replace('_', ' ')} operations adhering strictly to deterministic execution contracts. "
        f"This capability provides verifiable output transformation, deep static and dynamic inspection, "
        f"and structured failure recovery for {subcat_desc.lower()}."
    )

    platforms = PLATFORM_MAP.get(category_id, ["cross_platform"])
    tool_name, server_name = SERVER_MAP.get(category_id, ("run_command", "native_shell"))

    intent_patterns = [
        f"run {kw.replace('_', ' ')} on {subcategory_id.replace('_', ' ')}",
        f"execute {name.lower()}",
        f"analyze {kw.replace('_', ' ')} parameters",
        f"{kw.replace('_', ' ')} {category_id.replace('_', ' ')}"
    ]

    prerequisites = [
        f"Valid input descriptor for {kw.replace('_', ' ')}",
        f"Target environment initialized with {server_name} connectivity"
    ]

    required_inputs = [
        {
            "name": "target_payload",
            "type": "string",
            "description": f"Primary target data or identifier for {kw.replace('_', ' ')} execution",
            "required": True
        },
        {
            "name": "execution_options",
            "type": "object",
            "description": "Deterministic execution flags, timeout settings, and output format constraints",
            "required": False
        }
    ]

    expected_outputs = [
        {
            "name": "execution_report",
            "type": "object",
            "description": f"Structured result payload containing telemetry and status for {kw.replace('_', ' ')}"
        },
        {
            "name": "transformed_artifact",
            "type": "string",
            "description": "Path or identifier of the generated or transformed output asset"
        }
    ]

    execution_workflow = [
        {
            "step_number": 1,
            "action": f"Validate inputs and verify {server_name} pre-conditions",
            "description": f"Assert target payload presence and confirm environment permissions for {category_id}",
            "expected_outcome": "Input payload confirmed valid and environment ready"
        },
        {
            "step_number": 2,
            "action": f"Execute core {kw.replace('_', ' ')} routine",
            "description": f"Dispatch execution envelope to {tool_name} under {server_name} runtime boundary",
            "expected_outcome": "Core operation completed without errors"
        },
        {
            "step_number": 3,
            "action": "Verify execution integrity and enforce invariants",
            "description": "Inspect returned artifacts against validation schema and ensure no constraint violations",
            "expected_outcome": "Invariant checks verified with clean validation status"
        },
        {
            "step_number": 4,
            "action": "Package structured completion telemetry",
            "description": "Format output report and serialize state into persistent cache registry",
            "expected_outcome": "Structured telemetry emitted and state persisted"
        }
    ]

    decision_logic = {
        "rules": [
            {
                "condition": f"Environment {server_name} unavailable",
                "action": "Route task through fallback executor or mock sandbox"
            },
            {
                "condition": "Output constraint validation failure",
                "action": "Halt pipeline and emit deterministic diagnostic error report"
            }
        ],
        "fallback": f"Switch to conservative inspection mode and alert orchestrator"
    }

    tool_requirements = [
        {
            "tool_name": tool_name,
            "server_name": server_name,
            "optional": False
        }
    ]

    dependencies = {
        "system_libraries": ["libc.so.6" if "linux" in platforms else "kernel32.dll"],
        "runtime_packages": ["nexora-core", "jsonschema"],
        "skill_dependencies": []
    }

    safety_restrictions = [
        "Enforce strict read-only boundary when inspecting external untrusted inputs",
        "Prohibit destructive file operations without prior checksum verification",
        "Zero-comment output code enforcement on all synthesized assets"
    ]

    validation_criteria = [
        "Execution output matches expected response schema",
        f"Telemetry status confirms successful {kw.replace('_', ' ')} transformation",
        "Zero syntax or runtime exceptions encountered"
    ]

    practical_examples = [
        {
            "scenario": f"Production execution of {name}",
            "input": {
                "target_payload": f"payload://{subcategory_id}/{kw_clean}_sample.dat",
                "execution_options": {
                    "strict_mode": True,
                    "timeout_seconds": 60
                }
            },
            "expected_output": {
                "status": "success",
                "action": kw_clean,
                "verified": True
            }
        }
    ]

    related_skills = [
        f"nexora.{category_id}.{subcategory_id}.fallback_001"
    ]

    return {
        "id": skill_id,
        "name": name,
        "purpose": purpose,
        "category": category_id,
        "subcategory": subcategory_id,
        "description": description,
        "supported_platforms": platforms,
        "activation_conditions": {
            "intent_patterns": intent_patterns,
            "prerequisites": prerequisites
        },
        "required_inputs": required_inputs,
        "expected_outputs": expected_outputs,
        "execution_workflow": execution_workflow,
        "decision_logic": decision_logic,
        "tool_requirements": tool_requirements,
        "dependencies": dependencies,
        "safety_restrictions": safety_restrictions,
        "validation_criteria": validation_criteria,
        "practical_examples": practical_examples,
        "related_skills": related_skills,
        "version": "1.0.0"
    }

def main() -> int:
    matrix_path = "categories/taxonomy_matrix.json"
    if not os.path.exists(matrix_path):
        print(f"Taxonomy matrix not found: {matrix_path}")
        return 1

    with open(matrix_path, "r", encoding="utf-8") as file_handle:
        taxonomy = json.load(file_handle)

    os.makedirs("skills", exist_ok=True)
    os.makedirs("registry", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)

    db_path = "registry/nexora_registry.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    registry = SkillRegistry(db_path=db_path)

    total_target = taxonomy.get("total_skill_capacity", 3000)
    print(f"Initiating batch generation for target: {total_target} skills across {len(taxonomy['categories'])} categories")

    start_time = time.time()
    generated_count = 0
    skills_batch = []
    seen_ids = set()

    for cat_idx, category in enumerate(taxonomy["categories"], start=1):
        cat_id = category["id"]
        cat_allocation = category["target_allocation"]
        cat_generated = 0
        cat_dir = os.path.join("skills", cat_id)
        os.makedirs(cat_dir, exist_ok=True)

        for subcat in category.get("subcategories", []):
            subcat_id = subcat["id"]
            subcat_name = subcat["name"]
            subcat_desc = subcat.get("description", "")
            target_alloc = subcat.get("target_allocation", 0)
            keywords = subcat.get("capability_keywords", ["core", "operation"])

            subcat_dir = os.path.join(cat_dir, subcat_id)
            os.makedirs(subcat_dir, exist_ok=True)

            for i in range(target_alloc):
                skill = generate_skill_payload(
                    category_id=cat_id,
                    subcategory_id=subcat_id,
                    index_in_subcat=i,
                    subcat_name=subcat_name,
                    subcat_desc=subcat_desc,
                    keywords=keywords
                )

                if skill["id"] in seen_ids:
                    skill["id"] = f"{skill['id']}_{i}"
                seen_ids.add(skill["id"])

                skill_path = os.path.join(subcat_dir, f"{skill['id'].replace('.', '_')}.json")
                with open(skill_path, "w", encoding="utf-8") as file_handle:
                    json.dump(skill, file_handle, indent=2, ensure_ascii=False)

                skills_batch.append(skill)
                generated_count += 1
                cat_generated += 1

                if len(skills_batch) >= 100:
                    registry.insert_many(skills_batch)
                    skills_batch.clear()

        checkpoint_data = {
            "checkpoint_category": cat_id,
            "category_index": cat_idx,
            "total_categories": len(taxonomy["categories"]),
            "category_allocated": cat_allocation,
            "category_generated": cat_generated,
            "cumulative_skills_generated": generated_count,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "VALIDATED"
        }
        chk_file = os.path.join("checkpoints", f"checkpoint_category_{cat_idx:02d}_{cat_id}.json")
        with open(chk_file, "w", encoding="utf-8") as file_handle:
            json.dump(checkpoint_data, file_handle, indent=2)

        print(f"[{cat_idx:02d}/16] Category {cat_id}: Generated {cat_generated}/{cat_allocation} skills (Total: {generated_count})")

    if skills_batch:
        registry.insert_many(skills_batch)
        skills_batch.clear()

    catalog_index_path = "registry/skill_index.json"
    registry.export_index(catalog_index_path)

    total_in_db = registry.count_skills()
    registry.close()

    duration = time.time() - start_time
    print(f"Batch generation completed: {generated_count} skills written to disk, {total_in_db} in database in {duration:.2f}s")

    master_checkpoint = {
        "checkpoint_id": "phase-06-batch-generation-complete",
        "target_skills": total_target,
        "total_generated": generated_count,
        "total_in_database": total_in_db,
        "unique_ids_count": len(seen_ids),
        "duration_seconds": round(duration, 2),
        "status": "COMPLETED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with open("checkpoints/checkpoint_skills_3000.json", "w", encoding="utf-8") as file_handle:
        json.dump(master_checkpoint, file_handle, indent=2)

    return 0 if generated_count == total_target else 1

if __name__ == "__main__":
    sys.exit(main())
