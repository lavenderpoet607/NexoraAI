from typing import List, Dict, Optional, Any

class SearchEngine:
    def __init__(self, registry: Optional[Any] = None):
        self.registry = registry

    def _extract_skill_tokens(self, skill: Dict[str, Any]) -> set:
        tokens = set()
        tokens.add(skill.get("category", "").lower())
        tokens.add(skill.get("subcategory", "").lower())
        for pattern in skill.get("activation_conditions", {}).get("intent_patterns", []):
            for part in pattern.lower().split():
                tokens.add(part)
        for tool in skill.get("tool_requirements", []):
            tool_name = tool.get("tool_name", "")
            if tool_name:
                tokens.add(tool_name.lower())
            server_name = tool.get("server_name", "")
            if server_name:
                tokens.add(server_name.lower())
        return tokens

    def filter_skills(
        self,
        skills: List[Dict[str, Any]],
        category: Optional[str] = None,
        platform: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        filtered = []
        for skill in skills:
            if category and skill.get("category") != category:
                continue

            if platform:
                supported = skill.get("supported_platforms", [])
                if platform not in supported and "cross_platform" not in supported:
                    continue

            if capabilities:
                skill_tokens = self._extract_skill_tokens(skill)
                matched_capabilities = [cap for cap in capabilities if cap.lower() in skill_tokens]
                if not matched_capabilities:
                    continue

            if keyword and keyword.strip():
                terms = [term.lower() for term in keyword.split() if term.strip()]
                searchable_text = " ".join([
                    skill.get("name", ""),
                    skill.get("purpose", ""),
                    skill.get("subcategory", ""),
                    skill.get("description", "")
                ]).lower()
                if not any(term in searchable_text for term in terms):
                    continue

            filtered.append(skill)
            if limit is not None and len(filtered) >= limit:
                break

        return filtered

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        if not self.registry:
            return []

        if query and query.strip():
            fetch_limit = limit * 4 if (category or platform or capabilities) else limit
            candidates = self.registry.search_skills(query, limit=fetch_limit)
        elif category:
            candidates = self.registry.get_skills_by_category(category)
        elif platform:
            candidates = self.registry.get_skills_by_platform(platform)
        else:
            fetch_limit = limit * 4 if (category or platform or capabilities) else limit
            candidates = self.registry.list_skills(limit=fetch_limit)

        return self.filter_skills(
            candidates,
            category=category,
            platform=platform,
            capabilities=capabilities,
            keyword=None if (query and query.strip()) else None,
            limit=limit
        )

    def match_capabilities(
        self,
        required_tools: Optional[List[str]] = None,
        required_platforms: Optional[List[str]] = None,
        intent: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        if not self.registry:
            return []

        all_skills = self.registry.list_skills()
        scored_skills = []

        for skill in all_skills:
            score = 0
            supported = skill.get("supported_platforms", [])

            if required_platforms:
                if any(p in supported or p == "cross_platform" for p in required_platforms):
                    score += 30
                else:
                    continue

            if required_tools:
                skill_tools = [tool.get("tool_name", "") for tool in skill.get("tool_requirements", [])]
                matched_tools = set(required_tools).intersection(set(skill_tools))
                score += len(matched_tools) * 20

            if intent:
                intent_lower = intent.lower()
                intent_patterns = skill.get("activation_conditions", {}).get("intent_patterns", [])
                for pattern in intent_patterns:
                    if pattern.lower() in intent_lower or intent_lower in pattern.lower():
                        score += 25
                if skill.get("name", "").lower() in intent_lower:
                    score += 15
                if skill.get("purpose", "").lower() in intent_lower:
                    score += 10

            if score > 0:
                scored_skills.append((score, skill))

        scored_skills.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored_skills[:limit]]

    def suggest_skills(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.search(query=query, limit=limit)
