import os
import json
import time
import hashlib
from collections import OrderedDict
from typing import Any, Dict, Optional, List

class SmartCache:
    def __init__(self, cache_dir: str = "cache", max_memory_items: int = 1000):
        self.cache_dir = cache_dir
        self.max_memory_items = max_memory_items
        self.memory_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.file_metadata: Dict[str, Dict[str, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def compute_hash(self, content: Any) -> str:
        if isinstance(content, bytes):
            raw_bytes = content
        elif isinstance(content, str):
            raw_bytes = content.encode("utf-8")
        else:
            raw_bytes = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def _disk_path(self, cache_key: str) -> str:
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in cache_key)
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def _put_memory(self, key: str, record: Dict[str, Any]) -> None:
        if key in self.memory_cache:
            self.memory_cache.move_to_end(key)
        self.memory_cache[key] = record
        while len(self.memory_cache) > self.max_memory_items:
            self.memory_cache.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        if key in self.memory_cache:
            record = self.memory_cache[key]
            source_file = record.get("source_file")
            source_mtime = record.get("source_mtime")
            if source_file and os.path.exists(source_file):
                current_mtime = os.path.getmtime(source_file)
                if current_mtime != source_mtime:
                    self.invalidate(key)
                    self.misses += 1
                    return None
            self.memory_cache.move_to_end(key)
            self.hits += 1
            return record["value"]

        disk_path = self._disk_path(key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "r", encoding="utf-8") as file_handle:
                    record = json.load(file_handle)
                source_file = record.get("source_file")
                source_mtime = record.get("source_mtime")
                if source_file and os.path.exists(source_file):
                    current_mtime = os.path.getmtime(source_file)
                    if current_mtime != source_mtime:
                        self.invalidate(key)
                        self.misses += 1
                        return None
                self._put_memory(key, record)
                self.hits += 1
                return record["value"]
            except (json.JSONDecodeError, OSError):
                self.misses += 1
                return None

        self.misses += 1
        return None

    def set(self, key: str, value: Any, source_file: Optional[str] = None) -> str:
        content_hash = self.compute_hash(value)
        source_mtime = None
        if source_file and os.path.exists(source_file):
            source_mtime = os.path.getmtime(source_file)

        record = {
            "key": key,
            "hash": content_hash,
            "timestamp": time.time(),
            "source_file": source_file,
            "source_mtime": source_mtime,
            "value": value
        }
        self._put_memory(key, record)

        disk_path = self._disk_path(key)
        try:
            with open(disk_path, "w", encoding="utf-8") as file_handle:
                json.dump(record, file_handle, indent=2, ensure_ascii=False)
        except OSError:
            pass

        if source_file:
            self.file_metadata[source_file] = {
                "key": key,
                "mtime": source_mtime,
                "hash": content_hash
            }

        return content_hash

    def get_by_file(self, file_path: str) -> Optional[Any]:
        if not os.path.exists(file_path):
            self.misses += 1
            return None
        current_mtime = os.path.getmtime(file_path)
        file_meta = self.file_metadata.get(file_path)
        if file_meta and file_meta.get("mtime") != current_mtime:
            self.invalidate_file(file_path)
            self.misses += 1
            return None
        key = self.compute_hash(file_path)
        return self.get(key)

    def set_by_file(self, file_path: str, value: Any) -> str:
        key = self.compute_hash(file_path)
        return self.set(key, value, source_file=file_path)

    def invalidate(self, key: str) -> bool:
        removed = False
        if key in self.memory_cache:
            del self.memory_cache[key]
            removed = True
        disk_path = self._disk_path(key)
        if os.path.exists(disk_path):
            try:
                os.remove(disk_path)
                removed = True
            except OSError:
                pass
        tracked_files = [path for path, meta in self.file_metadata.items() if meta.get("key") == key]
        for tracked_path in tracked_files:
            del self.file_metadata[tracked_path]
        return removed

    def invalidate_file(self, file_path: str) -> bool:
        key = self.compute_hash(file_path)
        return self.invalidate(key)

    def clear(self) -> None:
        self.memory_cache.clear()
        self.file_metadata.clear()
        self.hits = 0
        self.misses = 0
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

    def clean_disk_cache(self) -> int:
        removed_count = 0
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except OSError:
                        pass
        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        disk_entries_count = 0
        if os.path.exists(self.cache_dir):
            disk_entries_count = len([f for f in os.listdir(self.cache_dir) if f.endswith(".json")])
        total_requests = self.hits + self.misses
        hit_ratio = round(self.hits / total_requests, 4) if total_requests > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_ratio": hit_ratio,
            "memory_entries": len(self.memory_cache),
            "disk_entries": disk_entries_count,
            "max_memory_items": self.max_memory_items
        }

    def inspect(self) -> List[Dict[str, Any]]:
        entries = []
        if os.path.exists(self.cache_dir):
            for filename in sorted(os.listdir(self.cache_dir)):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as file_handle:
                            record = json.load(file_handle)
                        entries.append({
                            "key": record.get("key"),
                            "hash": record.get("hash"),
                            "timestamp": record.get("timestamp"),
                            "source_file": record.get("source_file"),
                            "size_bytes": os.path.getsize(file_path)
                        })
                    except (json.JSONDecodeError, OSError):
                        pass
        return entries
