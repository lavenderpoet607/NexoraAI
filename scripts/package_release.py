import os
import sys

sys.path.insert(0, os.path.abspath("."))

import json
import hashlib
import zipfile
import time

def compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main() -> int:
    release_dir = "releases"
    os.makedirs(release_dir, exist_ok=True)

    print("Building Nexora AI Release 1.0.0...")

    index_path = "registry/skill_index.json"
    if not os.path.exists(index_path):
        print(f"Index not found: {index_path}")
        return 1

    catalog_release_path = os.path.join(release_dir, "nexora_skill_catalog_v1.0.0.json")
    with open(index_path, "r", encoding="utf-8") as src, open(catalog_release_path, "w", encoding="utf-8") as dst:
        data = json.load(src)
        json.dump(data, dst, separators=(",", ":"), ensure_ascii=False)

    zip_release_path = os.path.join(release_dir, "nexora_skills_bundle_v1.0.0.zip")
    with zipfile.ZipFile(zip_release_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("skills"):
            for file in files:
                if file.endswith(".json"):
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, ".")
                    zipf.write(full_p, rel_p)

    checksums = {
        "nexora_skill_catalog_v1.0.0.json": compute_sha256(catalog_release_path),
        "nexora_skills_bundle_v1.0.0.zip": compute_sha256(zip_release_path),
        "nexora_registry.db": compute_sha256("registry/nexora_registry.db")
    }

    manifest = {
        "release_version": "1.0.0",
        "release_name": "Nexora AI Universal Skills Ecosystem",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_skills": len(data.get("skills", [])),
        "artifacts": [
            {
                "file": "nexora_skill_catalog_v1.0.0.json",
                "sha256": checksums["nexora_skill_catalog_v1.0.0.json"],
                "description": "Minified universal skill catalog index"
            },
            {
                "file": "nexora_skills_bundle_v1.0.0.zip",
                "sha256": checksums["nexora_skills_bundle_v1.0.0.zip"],
                "description": "Complete bundle of 3,000 canonical skill JSON files"
            },
            {
                "file": "nexora_registry.db",
                "sha256": checksums["nexora_registry.db"],
                "description": "Pre-built SQLite database with FTS5 virtual table"
            }
        ]
    }

    manifest_path = os.path.join(release_dir, "RELEASE_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    checksums_txt_path = os.path.join(release_dir, "CHECKSUMS.sha256")
    with open(checksums_txt_path, "w", encoding="utf-8") as f:
        for filename, sha in checksums.items():
            f.write(f"{sha}  {filename}\n")

    print(f"Release v1.0.0 built successfully in {release_dir}/")
    return 0

if __name__ == "__main__":
    sys.exit(main())

