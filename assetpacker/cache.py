"""Asset build cache — tracks file hashes to skip unchanged assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional

CACHE_VERSION = 1


@dataclass
class CacheEntry:
    path: str
    hash: str
    size: int


@dataclass
class BuildCache:
    entries: Dict[str, CacheEntry] = field(default_factory=dict)
    version: int = CACHE_VERSION

    def is_changed(self, path: Path) -> bool:
        """Return True if the file is new or its hash has changed."""
        key = str(path)
        if key not in self.entries:
            return True
        return self.entries[key].hash != _hash_file(path)

    def update(self, path: Path) -> None:
        key = str(path)
        self.entries[key] = CacheEntry(
            path=key,
            hash=_hash_file(path),
            size=path.stat().st_size,
        )

    def remove(self, path: Path) -> None:
        self.entries.pop(str(path), None)

    def save(self, cache_file: Path) -> None:
        data = {
            "version": self.version,
            "entries": {
                k: {"path": v.path, "hash": v.hash, "size": v.size}
                for k, v in self.entries.items()
            },
        }
        cache_file.write_text(json.dumps(data, indent=2))

    @staticmethod
    def load(cache_file: Path) -> "BuildCache":
        if not cache_file.exists():
            return BuildCache()
        try:
            data = json.loads(cache_file.read_text())
            if data.get("version") != CACHE_VERSION:
                return BuildCache()
            entries = {
                k: CacheEntry(**v) for k, v in data.get("entries", {}).items()
            }
            return BuildCache(entries=entries)
        except (json.JSONDecodeError, TypeError, KeyError):
            return BuildCache()


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()
