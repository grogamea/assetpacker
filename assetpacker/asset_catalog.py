"""Asset catalog: builds a structured, queryable catalog from a manifest."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from assetpacker.scanner import AssetManifest


@dataclass
class CatalogEntry:
    path: Path
    category: str
    size_bytes: int
    stem: str = field(init=False)
    suffix: str = field(init=False)

    def __post_init__(self):
        self.stem = self.path.stem
        self.suffix = self.path.suffix.lower()

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "category": self.category,
            "size_bytes": self.size_bytes,
            "stem": self.stem,
            "suffix": self.suffix,
        }


@dataclass
class AssetCatalog:
    entries: List[CatalogEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    def by_category(self, category: str) -> List[CatalogEntry]:
        return [e for e in self.entries if e.category == category]

    def by_suffix(self, suffix: str) -> List[CatalogEntry]:
        normalized = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
        return [e for e in self.entries if e.suffix == normalized]

    def find_by_stem(self, stem: str) -> Optional[CatalogEntry]:
        for entry in self.entries:
            if entry.stem == stem:
                return entry
        return None

    def categories(self) -> List[str]:
        return sorted(set(e.category for e in self.entries))

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "categories": self.categories(),
            "entries": [e.to_dict() for e in self.entries],
        }


def build_catalog(manifest: AssetManifest) -> AssetCatalog:
    """Build an AssetCatalog from an AssetManifest."""
    entries: List[CatalogEntry] = []
    category_map: Dict[str, List[Path]] = {
        "images": manifest.images,
        "audio": manifest.audio,
        "fonts": manifest.fonts,
        "data": manifest.data,
        "other": manifest.other,
    }
    for category, paths in category_map.items():
        for path in paths:
            size = path.stat().st_size if path.exists() else 0
            entries.append(CatalogEntry(path=path, category=category, size_bytes=size))
    return AssetCatalog(entries=entries)
