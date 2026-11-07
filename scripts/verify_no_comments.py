import os
import sys
import ast
import json
import tokenize
from typing import List, Tuple, Dict

def strip_quoted_strings(line: str) -> str:
    result = []
    in_single = False
    in_double = False
    escaped = False
    for char in line:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if not in_single and not in_double:
            result.append(char)
    return "".join(result)

def check_python_file(file_path: str) -> List[Tuple[int, str]]:
    violations = []
    with open(file_path, "rb") as file_handle:
        try:
            tokens = tokenize.tokenize(file_handle.readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    violations.append((token.start[0], f"Python comment detected: {token.string.strip()}"))
        except tokenize.TokenError as token_error:
            violations.append((1, f"Tokenize error: {str(token_error)}"))

    with open(file_path, "r", encoding="utf-8") as file_handle:
        try:
            tree = ast.parse(file_handle.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        first_expr = node.body[0].value
                        if isinstance(first_expr, ast.Constant) and isinstance(first_expr.value, str):
                            violations.append((
                                node.body[0].lineno,
                                f"Docstring commentary detected: {first_expr.value[:40]!r}"
                            ))
        except SyntaxError as syntax_error:
            violations.append((syntax_error.lineno or 1, f"Syntax error: {str(syntax_error)}"))

    return violations

def check_json_file(file_path: str) -> List[Tuple[int, str]]:
    violations = []
    double_slash = chr(47) + chr(47)
    slash_star = chr(47) + chr(42)
    star_slash = chr(42) + chr(47)
    hash_char = chr(35)

    with open(file_path, "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    try:
        json.loads(content)
    except json.JSONDecodeError as decode_error:
        violations.append((decode_error.lineno, f"JSON syntax violation: {str(decode_error)}"))
        return violations

    for line_number, line in enumerate(content.splitlines(), start=1):
        unquoted = strip_quoted_strings(line)
        if double_slash in unquoted or slash_star in unquoted or star_slash in unquoted:
            violations.append((line_number, f"Comment marker detected in JSON: {line.strip()}"))
        elif unquoted.strip().startswith(hash_char):
            violations.append((line_number, f"Comment marker detected in JSON: {line.strip()}"))

    return violations

def check_generic_file(file_path: str, extension: str) -> List[Tuple[int, str]]:
    violations = []
    hash_char = chr(35)
    double_slash = chr(47) + chr(47)
    slash_star = chr(47) + chr(42)
    star_slash = chr(42) + chr(47)
    double_dash = chr(45) + chr(45)
    html_start = chr(60) + chr(33) + chr(45) + chr(45)
    html_end = chr(45) + chr(45) + chr(62)
    ps_start = chr(60) + chr(35)
    ps_end = chr(35) + chr(62)

    with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
        lines = file_handle.readlines()

    for line_number, line in enumerate(lines, start=1):
        unquoted = strip_quoted_strings(line)
        stripped = unquoted.strip()

        if extension in [".yaml", ".yml"]:
            if hash_char in unquoted:
                violations.append((line_number, f"YAML comment detected: {line.strip()}"))

        elif extension == ".sql":
            if double_dash in unquoted or slash_star in unquoted or star_slash in unquoted:
                violations.append((line_number, f"SQL comment detected: {line.strip()}"))

        elif extension == ".sh":
            if hash_char in unquoted:
                violations.append((line_number, f"Shell comment detected: {line.strip()}"))

        elif extension == ".ps1":
            if hash_char in unquoted or ps_start in unquoted or ps_end in unquoted:
                violations.append((line_number, f"PowerShell comment detected: {line.strip()}"))

        if html_start in unquoted or html_end in unquoted:
            violations.append((line_number, f"HTML comment detected: {line.strip()}"))
        if double_slash in unquoted and extension not in [".json"]:
            violations.append((line_number, f"Slash comment detected: {line.strip()}"))

    return violations

def audit_repository(root_directory: str = ".") -> Dict[str, Any]:
    target_extensions = {".py", ".json", ".yaml", ".yml", ".sql", ".sh", ".ps1"}
    ignored_directories = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
        "node_modules",
        ".gemini"
    }

    scanned_files = 0
    violations_by_file: Dict[str, List[Tuple[int, str]]] = {}

    for dirpath, dirnames, filenames in os.walk(root_directory):
        dirnames[:] = [d for d in dirnames if d not in ignored_directories]

        for filename in sorted(filenames):
            extension = os.path.splitext(filename)[1].lower()
            if extension not in target_extensions:
                continue

            file_path = os.path.join(dirpath, filename)
            scanned_files += 1

            if extension == ".py":
                issues = check_python_file(file_path)
            elif extension == ".json":
                issues = check_json_file(file_path)
            else:
                issues = check_generic_file(file_path, extension)

            if issues:
                violations_by_file[file_path] = issues

    total_violations = sum(len(issues) for issues in violations_by_file.values())
    return {
        "scanned_files": scanned_files,
        "total_violations": total_violations,
        "violations": violations_by_file
    }

def main() -> int:
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    report = audit_repository(target_dir)

    print(f"Scanned files: {report['scanned_files']}")
    print(f"Total comment violations: {report['total_violations']}")

    if report["total_violations"] > 0:
        print("VIOLATIONS DETECTED:")
        for file_path, issues in report["violations"].items():
            print(f"File: {file_path}")
            for line_no, message in issues:
                print(f"  Line {line_no}: {message}")
        return 1

    print("SUCCESS: Strictly ZERO comments detected across audited repository files.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
