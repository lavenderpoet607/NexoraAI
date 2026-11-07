import os
import json
import jsonschema
from typing import Tuple, List, Dict, Any, Optional

class SkillValidator:
    def __init__(self, schema_path: Optional[str] = None):
        self.schema_path = schema_path or self._resolve_default_schema_path()
        self.schema = self._load_schema(self.schema_path)
        self.validator = jsonschema.Draft7Validator(self.schema)

    def _resolve_default_schema_path(self) -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.abspath(os.path.join(current_dir, "..", "schemas", "skill_schema.json")),
            os.path.abspath("schemas/skill_schema.json"),
            "schemas/skill_schema.json"
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]

    def _load_schema(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Skill schema file not found at: {path}")
        with open(path, "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)

    def validate_skill(self, skill_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        for error in self.validator.iter_errors(skill_dict):
            path_string = " -> ".join(str(elem) for elem in error.path) if error.path else "root"
            errors.append(f"[{path_string}]: {error.message}")
        return (len(errors) == 0, errors)

    def validate_file(self, file_path: str) -> Tuple[bool, List[str]]:
        if not os.path.exists(file_path):
            return (False, [f"File not found: {file_path}"])
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                skill_dict = json.load(file_handle)
        except json.JSONDecodeError as decode_error:
            return (False, [f"JSON parsing error: {str(decode_error)}"])
        except OSError as os_error:
            return (False, [f"IO error: {str(os_error)}"])
        return self.validate_skill(skill_dict)

    def validate_directory(self, directory_path: str) -> Dict[str, Any]:
        if not os.path.exists(directory_path):
            return {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "valid_files": [],
                "invalid_files": [],
                "errors": {"directory": [f"Directory not found: {directory_path}"]}
            }

        valid_files: List[str] = []
        invalid_files: List[str] = []
        errors_by_file: Dict[str, List[str]] = {}

        for root_dir, _, filenames in os.walk(directory_path):
            for filename in sorted(filenames):
                if filename.endswith(".json"):
                    full_path = os.path.join(root_dir, filename)
                    is_valid, error_list = self.validate_file(full_path)
                    if is_valid:
                        valid_files.append(full_path)
                    else:
                        invalid_files.append(full_path)
                        errors_by_file[full_path] = error_list

        return {
            "total": len(valid_files) + len(invalid_files),
            "valid": len(valid_files),
            "invalid": len(invalid_files),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "errors": errors_by_file
        }

    def validate_all(self, skills_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_count = 0
        invalid_count = 0
        errors_map: Dict[str, List[str]] = {}

        for index, skill in enumerate(skills_list):
            skill_id = skill.get("id", f"index_{index}")
            is_valid, errors = self.validate_skill(skill)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                errors_map[skill_id] = errors

        return {
            "total": len(skills_list),
            "valid": valid_count,
            "invalid": invalid_count,
            "errors": errors_map
        }
