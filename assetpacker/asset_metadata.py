"""Asset metadata extraction and storage."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AssetMetadata:
    path: Path
    size_bytes: int
    extension: str
    category: str
    tags: List[str] = field(default_factory=list)
    extra: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.extension = self.extension.lower().lstrip(".")

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def size_kb(self) -> float:
        return round(self.size_bytes / 1024, 2)

    def to_dict(self) -> Dict[str, object]:
        return {
            "path": str(self.path),
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "size_kb": self.size_kb,
            "extension": self.extension,
            "category": self.category,
            "tags": list(self.tags),
            "extra": dict(self.extra),
        }


_CATEGORY_MAP: Dict[str, str] = {
    "png": "image", "jpg": "image", "jpeg": "image", "gif": "image", "webp": "image",
    "mp3": "audio", "ogg": "audio", "wav": "audio", "flac": "audio",
    "ttf": "font", "otf": "font", "woff": "font", "woff2": "font",
    "json": "data", "xml": "data", "csv": "data", "yaml": "data", "yml": "data",
    "glsl": "shader", "vert": "shader", "frag": "shader",
}


def _infer_category(ext: str) -> str:
    return _CATEGORY_MAP.get(ext.lower().lstrip("."), "other")


def extract_metadata(path: Path, tags: Optional[List[str]] = None) -> AssetMetadata:
    """Extract metadata from a single asset file."""
    if not path.exists():
        raise FileNotFoundError(f"Asset not found: {path}")
    stat = path.stat()
    ext = path.suffix.lstrip(".")
    return AssetMetadata(
        path=path,
        size_bytes=stat.st_size,
        extension=ext,
        category=_infer_category(ext),
        tags=list(tags or []),
    )


def extract_all(paths: List[Path]) -> List[AssetMetadata]:
    """Extract metadata for a list of asset paths."""
    results = []
    for p in paths:
        try:
            results.append(extract_metadata(p))
        except FileNotFoundError:
            pass
    return results
