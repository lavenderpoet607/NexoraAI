import os
import json
import sqlite3
from typing import List, Dict, Optional, Any

class SkillRegistry:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "registry/nexora_registry.db"
        self._connection: Optional[sqlite3.Connection] = None
        self.initialize_db(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            directory = os.path.dirname(self.db_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.execute("PRAGMA synchronous = NORMAL")
        return self._connection

    def initialize_db(self, db_path: Optional[str] = None) -> None:
        if db_path is not None:
            if self._connection is not None:
                self._connection.close()
                self._connection = None
            self.db_path = db_path

        connection = self._get_connection()
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    description TEXT NOT NULL,
                    supported_platforms TEXT NOT NULL,
                    data TEXT NOT NULL,
                    version TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
                    id UNINDEXED,
                    name,
                    purpose,
                    category,
                    subcategory,
                    description
                )
            """)
            connection.execute("CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_skills_subcategory ON skills(subcategory)")

    def insert_skill(self, skill_dict: Dict[str, Any]) -> bool:
        skill_id = skill_dict.get("id")
        if not skill_id:
            raise ValueError("Skill dictionary must contain a valid id field")

        name = skill_dict.get("name", "")
        purpose = skill_dict.get("purpose", "")
        category = skill_dict.get("category", "")
        subcategory = skill_dict.get("subcategory", "")
        description = skill_dict.get("description", "")
        platforms = json.dumps(skill_dict.get("supported_platforms", []))
        version = skill_dict.get("version", "1.0.0")
        data = json.dumps(skill_dict, ensure_ascii=False)

        connection = self._get_connection()
        with connection:
            connection.execute("""
                INSERT OR REPLACE INTO skills (
                    id, name, purpose, category, subcategory, description, supported_platforms, data, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (skill_id, name, purpose, category, subcategory, description, platforms, data, version))
            connection.execute("DELETE FROM skills_fts WHERE id = ?", (skill_id,))
            connection.execute("""
                INSERT INTO skills_fts (id, name, purpose, category, subcategory, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_id, name, purpose, category, subcategory, description))
        return True

    def insert_many(self, skills_list: List[Dict[str, Any]]) -> int:
        connection = self._get_connection()
        inserted_count = 0
        with connection:
            for skill_dict in skills_list:
                skill_id = skill_dict.get("id")
                if not skill_id:
                    continue
                name = skill_dict.get("name", "")
                purpose = skill_dict.get("purpose", "")
                category = skill_dict.get("category", "")
                subcategory = skill_dict.get("subcategory", "")
                description = skill_dict.get("description", "")
                platforms = json.dumps(skill_dict.get("supported_platforms", []))
                version = skill_dict.get("version", "1.0.0")
                data = json.dumps(skill_dict, ensure_ascii=False)

                connection.execute("""
                    INSERT OR REPLACE INTO skills (
                        id, name, purpose, category, subcategory, description, supported_platforms, data, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (skill_id, name, purpose, category, subcategory, description, platforms, data, version))
                connection.execute("DELETE FROM skills_fts WHERE id = ?", (skill_id,))
                connection.execute("""
                    INSERT INTO skills_fts (id, name, purpose, category, subcategory, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (skill_id, name, purpose, category, subcategory, description))
                inserted_count += 1
        return inserted_count

    def get_skill_by_id(self, skill_id: str) -> Optional[Dict[str, Any]]:
        connection = self._get_connection()
        cursor = connection.execute("SELECT data FROM skills WHERE id = ?", (skill_id,))
        row = cursor.fetchone()
        if row is not None:
            return json.loads(row["data"])
        return None

    def search_skills(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return self.list_skills(limit=limit)

        connection = self._get_connection()
        sanitized = "".join(character if character.isalnum() or character in " _-" else " " for character in query).strip()
        tokens = [token for token in sanitized.split() if token]
        if not tokens:
            return self.list_skills(limit=limit)

        fts_match_query = " ".join(f'"{token}"*' for token in tokens)
        try:
            cursor = connection.execute("""
                SELECT s.data
                FROM skills_fts f
                JOIN skills s ON f.id = s.id
                WHERE skills_fts MATCH ?
                ORDER BY bm25(skills_fts)
                LIMIT ?
            """, (fts_match_query, limit))
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            cursor = connection.execute("""
                SELECT data FROM skills
                WHERE name LIKE ? OR purpose LIKE ? OR description LIKE ?
                ORDER BY id ASC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            rows = cursor.fetchall()

        return [json.loads(row["data"]) for row in rows]

    def list_categories(self) -> List[str]:
        connection = self._get_connection()
        cursor = connection.execute("SELECT DISTINCT category FROM skills ORDER BY category ASC")
        return [row["category"] for row in cursor.fetchall()]

    def get_skills_by_category(self, category: str) -> List[Dict[str, Any]]:
        connection = self._get_connection()
        cursor = connection.execute("SELECT data FROM skills WHERE category = ? ORDER BY id ASC", (category,))
        return [json.loads(row["data"]) for row in cursor.fetchall()]

    def get_skills_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        connection = self._get_connection()
        cursor = connection.execute("SELECT data, supported_platforms FROM skills ORDER BY id ASC")
        matching_skills = []
        for row in cursor.fetchall():
            platforms = json.loads(row["supported_platforms"])
            if platform in platforms or "cross_platform" in platforms:
                matching_skills.append(json.loads(row["data"]))
        return matching_skills

    def list_skills(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        connection = self._get_connection()
        if limit is not None:
            cursor = connection.execute("SELECT data FROM skills ORDER BY id ASC LIMIT ? OFFSET ?", (limit, offset))
        else:
            cursor = connection.execute("SELECT data FROM skills ORDER BY id ASC")
        return [json.loads(row["data"]) for row in cursor.fetchall()]

    def count_skills(self) -> int:
        connection = self._get_connection()
        cursor = connection.execute("SELECT COUNT(*) AS total_count FROM skills")
        row = cursor.fetchone()
        return row["total_count"] if row is not None else 0

    def delete_skill(self, skill_id: str) -> bool:
        connection = self._get_connection()
        with connection:
            connection.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
            connection.execute("DELETE FROM skills_fts WHERE id = ?", (skill_id,))
        return True

    def export_index(self, output_json_path: str) -> int:
        all_skills = self.list_skills()
        directory = os.path.dirname(output_json_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        payload = {
            "total_skills": len(all_skills),
            "skills": all_skills
        }
        with open(output_json_path, "w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=2, ensure_ascii=False)
        return len(all_skills)

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
