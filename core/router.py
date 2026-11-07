from typing import Dict, List, Optional, Any
from core.search import SearchEngine

class TaskRouter:
    def __init__(self, registry: Optional[Any] = None, search_engine: Optional[Any] = None):
        self.registry = registry
        self.search_engine = search_engine or (SearchEngine(registry) if registry else None)
        self.domain_agent_map: Dict[str, str] = {
            "binary_analysis_and_reverse_engineering": "binary_reverse_engineering_agent",
            "mobile_security_and_app_analysis": "mobile_app_sec_agent",
            "game_development_and_virtual_worlds": "game_world_developer_agent",
            "three_dimensional_graphics_and_animation": "three_d_media_agent",
            "cybersecurity_and_penetration_testing": "cybersecurity_analyst_agent",
            "system_architecture_and_os_internals": "nexora-architect",
            "software_engineering_and_architecture": "code_synthesis_engineer_agent",
            "web_technologies_and_browser_automation": "nexora-swe",
            "ai_ml_and_cognitive_orchestration": "nexora-architect",
            "cloud_devops_and_infrastructure": "nexora-swe",
            "data_engineering_and_storage_systems": "storage_indexing_agent",
            "hardware_embedded_and_iot": "binary_reverse_engineering_agent",
            "network_protocols_and_traffic_analysis": "cybersecurity_analyst_agent",
            "media_processing_and_creative_automation": "three_d_media_agent",
            "security_governance_and_compliance": "verification_qa_agent",
            "autonomous_agent_orchestration_and_routing": "nexora-architect"
        }
        self.default_agent = "nexora-swe"

    def estimate_tokens(self, prompt: str, context: Optional[str] = None) -> int:
        prompt_words = len(prompt.split())
        context_words = len((context or "").split())
        return int((prompt_words + context_words) * 1.35)

    def analyze_complexity(
        self,
        prompt: str,
        context: Optional[str] = None,
        estimated_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        total_tokens = estimated_tokens if estimated_tokens is not None else self.estimate_tokens(prompt, context)
        prompt_lower = prompt.lower()

        large_indicators = [
            "3000 skills",
            "entire repository",
            "all categories",
            "batch generator",
            "full ecosystem",
            "complete migration",
            "global scan"
        ]
        complex_indicators = [
            "pipeline",
            "orchestrate",
            "multi-step",
            "cross-platform",
            "reverse engineer",
            "decompile and patch",
            "full test suite",
            "dynamic hooking"
        ]

        if total_tokens >= 16000 or any(indicator in prompt_lower for indicator in large_indicators):
            complexity = "LARGE"
            reason = "Task scope requires multi-subagent mesh coordination across full repository scale"
        elif total_tokens >= 4000 or any(indicator in prompt_lower for indicator in complex_indicators):
            complexity = "COMPLEX"
            reason = "Task involves multi-domain workflow and sequential execution pipeline"
        elif total_tokens >= 1000 or len(prompt.split()) > 35:
            complexity = "MEDIUM"
            reason = "Task requires domain-specific reasoning and specialized tool invocation"
        else:
            complexity = "SIMPLE"
            reason = "Task is atomic and directly resolvable via single skill execution"

        return {
            "complexity": complexity,
            "estimated_tokens": total_tokens,
            "reason": reason
        }

    def detect_domain(self, prompt: str) -> Optional[str]:
        prompt_lower = prompt.lower()
        domain_keywords = {
            "binary_analysis_and_reverse_engineering": [
                "disassemble", "decompile", "ida", "binary", "assembly", "cfg", "patch", "smali", "bytecode"
            ],
            "mobile_security_and_app_analysis": [
                "android", "apk", "adb", "frida", "hooking", "ios", "jailbreak"
            ],
            "game_development_and_virtual_worlds": [
                "roblox", "luau", "game", "avatar", "physics", "studio", "rbxm"
            ],
            "three_dimensional_graphics_and_animation": [
                "blender", "mesh", "3d", "rigging", "animation", "render", "shader"
            ],
            "cybersecurity_and_penetration_testing": [
                "pcap", "penetration", "exploit", "cve", "traffic", "vulnerability", "wireshark"
            ],
            "software_engineering_and_architecture": [
                "refactor", "ast", "cli", "architecture", "synthesis", "unittest", "registry", "cache"
            ],
            "data_engineering_and_storage_systems": [
                "sqlite", "fts5", "cache", "lru", "storage", "database", "indexing", "sha-256"
            ],
            "security_governance_and_compliance": [
                "validation", "schema", "zero comment", "compliance", "audit", "jsonschema"
            ]
        }

        best_domain = None
        best_count = 0
        for domain, keywords in domain_keywords.items():
            count = sum(1 for keyword in keywords if keyword in prompt_lower)
            if count > best_count:
                best_count = count
                best_domain = domain

        return best_domain if best_count > 0 else None

    def recommend_delegation(self, complexity: str, domain: Optional[str] = None) -> Dict[str, Any]:
        primary = self.domain_agent_map.get(domain, self.default_agent) if domain else self.default_agent

        if complexity == "SIMPLE":
            return {
                "execution_mode": "direct",
                "primary_agent": primary,
                "support_agents": [],
                "workflow_steps": [
                    "Validate single input payload",
                    "Execute atomic skill",
                    "Format direct result"
                ]
            }
        elif complexity == "MEDIUM":
            return {
                "execution_mode": "single_subagent",
                "primary_agent": primary,
                "support_agents": ["verification_qa_agent"],
                "workflow_steps": [
                    "Parse intent and load skill dependencies",
                    "Execute primary subagent workflow",
                    "Validate output against criteria",
                    "Synthesize completion response"
                ]
            }
        elif complexity == "COMPLEX":
            return {
                "execution_mode": "pipeline",
                "primary_agent": "nexora-architect",
                "support_agents": [primary, "verification_qa_agent"],
                "workflow_steps": [
                    "Analyze architectural boundaries and partition stages",
                    "Dispatch subagent pipeline execution",
                    "Enforce zero-comment and schema validation rules",
                    "Aggregate multi-step deliverables into structured report"
                ]
            }
        else:
            return {
                "execution_mode": "parallel_mesh",
                "primary_agent": "nexora-architect",
                "support_agents": [
                    "nexora-swe",
                    "nexora-research",
                    "verification_qa_agent",
                    "storage_indexing_agent"
                ],
                "workflow_steps": [
                    "Formulate distributed task manifest",
                    "Dispatch parallel subagent workloads with checkpointing",
                    "Index generated skills into SQLite FTS5 database",
                    "Execute repository-wide test suite and compliance audit",
                    "Publish release package"
                ]
            }

    def select_skills(self, prompt: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self.search_engine is not None:
            return self.search_engine.search(query=prompt, limit=limit)
        if self.registry is not None:
            return self.registry.search_skills(prompt, limit=limit)
        return []

    def route_task(
        self,
        prompt: str,
        context: Optional[str] = None,
        estimated_tokens: Optional[int] = None,
        limit_skills: int = 5
    ) -> Dict[str, Any]:
        complexity_info = self.analyze_complexity(prompt, context=context, estimated_tokens=estimated_tokens)
        domain = self.detect_domain(prompt)
        delegation = self.recommend_delegation(complexity_info["complexity"], domain=domain)
        matching_skills = self.select_skills(prompt, limit=limit_skills)

        return {
            "prompt": prompt,
            "complexity": complexity_info["complexity"],
            "estimated_tokens": complexity_info["estimated_tokens"],
            "complexity_reason": complexity_info["reason"],
            "detected_domain": domain,
            "primary_agent": delegation["primary_agent"],
            "support_agents": delegation["support_agents"],
            "execution_mode": delegation["execution_mode"],
            "workflow_steps": delegation["workflow_steps"],
            "matching_skills": matching_skills
        }
