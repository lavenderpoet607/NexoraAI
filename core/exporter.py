import os
import json
from typing import List, Dict, Any, Optional

class PlatformExporter:
    def __init__(self, output_root: str = "platforms"):
        self.output_root = output_root

    def export_antigravity(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        exported_files = []
        for skill in skills:
            skill_id = skill.get("id", "unknown_skill")
            skill_dir = os.path.join(target_dir, skill_id.replace(".", "_"))
            os.makedirs(skill_dir, exist_ok=True)
            doc_path = os.path.join(skill_dir, "SKILL.md")

            content = [
                "---",
                f"name: {skill.get('name')}",
                f"description: {skill.get('purpose')}",
                f"category: {skill.get('category')}",
                f"subcategory: {skill.get('subcategory')}",
                f"version: {skill.get('version')}",
                "---",
                "",
                f"# {skill.get('name')}",
                "",
                "## Purpose",
                skill.get("purpose", ""),
                "",
                "## Description",
                skill.get("description", ""),
                "",
                "## Supported Platforms",
                ", ".join(skill.get("supported_platforms", [])),
                "",
                "## Activation Conditions",
                "### Intent Patterns",
            ]
            for pattern in skill.get("activation_conditions", {}).get("intent_patterns", []):
                content.append(f"- {pattern}")
            content.append("")
            content.append("### Prerequisites")
            for req in skill.get("activation_conditions", {}).get("prerequisites", []):
                content.append(f"- {req}")
            content.append("")

            content.append("## Required Inputs")
            for inp in skill.get("required_inputs", []):
                content.append(f"- **{inp.get('name')}** ({inp.get('type')}): {inp.get('description')}")
            content.append("")

            content.append("## Expected Outputs")
            for out in skill.get("expected_outputs", []):
                content.append(f"- **{out.get('name')}** ({out.get('type')}): {out.get('description')}")
            content.append("")

            content.append("## Execution Workflow")
            for step in skill.get("execution_workflow", []):
                content.append(f"{step.get('step_number')}. **{step.get('action')}**: {step.get('description')}")
            content.append("")

            content.append("## Decision Logic")
            content.append(f"- **Fallback**: {skill.get('decision_logic', {}).get('fallback', '')}")
            for rule in skill.get("decision_logic", {}).get("rules", []):
                content.append(f"- **If**: {rule.get('condition')} -> **Then**: {rule.get('action')}")
            content.append("")

            content.append("## Safety Restrictions")
            for safety in skill.get("safety_restrictions", []):
                content.append(f"- {safety}")
            content.append("")

            content.append("## Validation Criteria")
            for val in skill.get("validation_criteria", []):
                content.append(f"- {val}")
            content.append("")

            with open(doc_path, "w", encoding="utf-8") as file_handle:
                file_handle.write("\n".join(content) + "\n")
            exported_files.append(doc_path)

        return exported_files

    def export_claude_code(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        claude_md_path = os.path.join(target_dir, "CLAUDE.md")
        lines = [
            "# NEXORA AI Skills for Claude Code",
            "",
            "## Active Capabilities",
            "",
        ]
        for skill in skills:
            lines.append(f"### {skill.get('name')} (`{skill.get('id')}`)")
            lines.append(f"- **Purpose**: {skill.get('purpose')}")
            lines.append(f"- **Category**: {skill.get('category')} / {skill.get('subcategory')}")
            lines.append("- **Activation Trigger**:")
            for p in skill.get("activation_conditions", {}).get("intent_patterns", []):
                lines.append(f"  - `{p}`")
            lines.append("- **Workflow**:")
            for s in skill.get("execution_workflow", []):
                lines.append(f"  {s.get('step_number')}. {s.get('action')}")
            lines.append("")

        with open(claude_md_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [claude_md_path]

    def export_cursor(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        rules_dir = os.path.join(target_dir, ".cursor", "rules")
        os.makedirs(rules_dir, exist_ok=True)
        exported = []
        for skill in skills:
            rule_file = os.path.join(rules_dir, f"{skill.get('id', 'skill').replace('.', '_')}.mdc")
            content = [
                "---",
                f"description: {skill.get('purpose')}",
                "globs: *",
                "alwaysApply: false",
                "---",
                "",
                f"# {skill.get('name')}",
                "",
                skill.get("description", ""),
                "",
                "## Activation",
                ", ".join(skill.get("activation_conditions", {}).get("intent_patterns", [])),
                "",
                "## Instructions",
            ]
            for step in skill.get("execution_workflow", []):
                content.append(f"{step.get('step_number')}. {step.get('action')}: {step.get('description')}")
            content.append("")
            with open(rule_file, "w", encoding="utf-8") as file_handle:
                file_handle.write("\n".join(content) + "\n")
            exported.append(rule_file)
        return exported

    def export_windsurf(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        rule_path = os.path.join(target_dir, ".windsurfrules")
        lines = [
            "# NEXORA AI Rules for Windsurf Cascade",
            "",
            "## Rules and Capabilities",
            "",
        ]
        for skill in skills:
            lines.append(f"- **{skill.get('name')}**: {skill.get('purpose')}")
            for step in skill.get("execution_workflow", []):
                lines.append(f"  - Step {step.get('step_number')}: {step.get('action')}")
        lines.append("")
        with open(rule_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [rule_path]

    def export_copilot(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        github_dir = os.path.join(target_dir, ".github")
        os.makedirs(github_dir, exist_ok=True)
        instruction_path = os.path.join(github_dir, "copilot-instructions.md")
        lines = [
            "# GitHub Copilot Coding Instructions",
            "",
            "## Nexora AI Skill Directives",
            "",
        ]
        for skill in skills:
            lines.append(f"### {skill.get('name')}")
            lines.append(f"When executing tasks matching: {', '.join(skill.get('activation_conditions', {}).get('intent_patterns', []))}")
            lines.append(f"Follow workflow: {skill.get('purpose')}")
            for step in skill.get("execution_workflow", []):
                lines.append(f"- {step.get('action')}")
            lines.append("")
        with open(instruction_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [instruction_path]

    def export_cline(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        cline_path = os.path.join(target_dir, ".clinerules")
        lines = [
            "# Cline System Rules - Nexora AI",
            "",
            "## Skill Catalog",
            "",
        ]
        for skill in skills:
            lines.append(f"### {skill.get('name')} (`{skill.get('id')}`)")
            lines.append(f"Goal: {skill.get('purpose')}")
            lines.append("Steps:")
            for s in skill.get("execution_workflow", []):
                lines.append(f"1. {s.get('action')}: {s.get('description')}")
            lines.append("")
        with open(cline_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [cline_path]

    def export_roo_code(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        roo_path = os.path.join(target_dir, ".roomodes")
        modes = []
        for skill in skills:
            modes.append({
                "slug": skill.get("id", "skill").replace(".", "-"),
                "name": skill.get("name"),
                "roleDefinition": skill.get("purpose"),
                "customInstructions": skill.get("description"),
                "groups": ["read", "edit", "command"]
            })
        with open(roo_path, "w", encoding="utf-8") as file_handle:
            json.dump({"customModes": modes}, file_handle, indent=2)
        return [roo_path]

    def export_gemini_cli(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        gemini_path = os.path.join(target_dir, "GEMINI.md")
        lines = [
            "# Gemini CLI Instructions - Nexora AI",
            "",
            "## Registered Skills",
            "",
        ]
        for skill in skills:
            lines.append(f"### {skill.get('name')}")
            lines.append(f"Purpose: {skill.get('purpose')}")
            lines.append(f"Workflow: {', '.join(s.get('action') for s in skill.get('execution_workflow', []))}")
            lines.append("")
        with open(gemini_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [gemini_path]

    def export_codex(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        codex_path = os.path.join(target_dir, "codex_prompt.md")
        lines = [
            "# OpenAI Codex Skill Prompt",
            "",
            "## Available Agent Functions",
            "",
        ]
        for skill in skills:
            lines.append(f"Function: {skill.get('id')}")
            lines.append(f"Name: {skill.get('name')}")
            lines.append(f"Doc: {skill.get('purpose')}")
            lines.append("")
        with open(codex_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")
        return [codex_path]

    def export_continue(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        continue_dir = os.path.join(target_dir, ".continue")
        os.makedirs(continue_dir, exist_ok=True)
        cfg_path = os.path.join(continue_dir, "config.json")
        rules = []
        for skill in skills:
            rules.append(f"{skill.get('name')}: {skill.get('purpose')}")
        cfg = {
            "customCommands": [
                {
                    "name": s.get("id", "cmd").replace(".", "-"),
                    "prompt": s.get("purpose"),
                    "description": s.get("name")
                } for s in skills
            ],
            "systemMessage": "\n".join(rules[:50])
        }
        with open(cfg_path, "w", encoding="utf-8") as file_handle:
            json.dump(cfg, file_handle, indent=2)
        return [cfg_path]

    def export_aider(self, skills: List[Dict[str, Any]], target_dir: str) -> List[str]:
        os.makedirs(target_dir, exist_ok=True)
        conventions_path = os.path.join(target_dir, "CONVENTIONS.md")
        conf_path = os.path.join(target_dir, ".aider.conf.yml")

        lines = [
            "# Project Conventions - Nexora AI",
            "",
            "## Coding Standards and Directives",
            "",
        ]
        for skill in skills:
            lines.append(f"- **{skill.get('name')}**: {skill.get('purpose')}")
        lines.append("")

        with open(conventions_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")

        with open(conf_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("read:\n  - CONVENTIONS.md\nauto-commits: true\n")

        return [conventions_path, conf_path]

    def export_all(self, skills: List[Dict[str, Any]], base_dir: Optional[str] = None) -> Dict[str, List[str]]:
        root = base_dir or self.output_root
        results = {}
        results["google_antigravity"] = self.export_antigravity(skills, os.path.join(root, "antigravity"))
        results["claude_code"] = self.export_claude_code(skills, os.path.join(root, "claude_code"))
        results["cursor"] = self.export_cursor(skills, os.path.join(root, "cursor"))
        results["windsurf"] = self.export_windsurf(skills, os.path.join(root, "windsurf"))
        results["github_copilot"] = self.export_copilot(skills, os.path.join(root, "copilot"))
        results["cline"] = self.export_cline(skills, os.path.join(root, "cline"))
        results["roo_code"] = self.export_roo_code(skills, os.path.join(root, "roo_code"))
        results["gemini_cli"] = self.export_gemini_cli(skills, os.path.join(root, "gemini_cli"))
        results["openai_codex"] = self.export_codex(skills, os.path.join(root, "codex"))
        results["continue"] = self.export_continue(skills, os.path.join(root, "continue"))
        results["aider"] = self.export_aider(skills, os.path.join(root, "aider"))
        return results

