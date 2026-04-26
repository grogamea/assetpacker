"""Persistent metadata store — save and load asset metadata as JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from assetpacker.asset_metadata import AssetMetadata, extract_metadata


class MetadataStore:
    """Holds extracted metadata for all assets and can persist to disk."""

    def __init__(self) -> None:
        self._entries: Dict[str, AssetMetadata] = {}

    # ------------------------------------------------------------------
    def add(self, meta: AssetMetadata) -> None:
        self._entries[str(meta.path)] = meta

    def get(self, path: Path) -> Optional[AssetMetadata]:
        return self._entries.get(str(path))

    def remove(self, path: Path) -> None:
        self._entries.pop(str(path), None)

    def all(self) -> List[AssetMetadata]:
        return list(self._entries.values())

    def by_category(self, category: str) -> List[AssetMetadata]:
        return [m for m in self._entries.values() if m.category == category]

    def categories(self) -> List[str]:
        return sorted({m.category for m in self._entries.values()})

    # ------------------------------------------------------------------
    def save(self, dest: Path) -> None:
        """Serialise the store to a JSON file."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = [m.to_dict() for m in self._entries.values()]
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, src: Path) -> "MetadataStore":
        """Deserialise a store from a JSON file produced by :meth:`save`."""
        store = cls()
        if not src.exists():
            return store
        raw = json.loads(src.read_text(encoding="utf-8"))
        for item in raw:
            meta = AssetMetadata(
                path=Path(item["path"]),
                size_bytes=item["size_bytes"],
                extension=item["extension"],
                category=item["category"],
                tags=item.get("tags", []),
                extra=item.get("extra", {}),
            )
            store.add(meta)
        return store


def build_store(paths: List[Path]) -> MetadataStore:
    """Convenience: extract metadata for every path and return a populated store."""
    store = MetadataStore()
    for p in paths:
        try:
            store.add(extract_metadata(p))
        except FileNotFoundError:
            pass
    return store
