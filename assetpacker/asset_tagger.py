"""Automatic asset tagging based on file properties and path patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from assetpacker.scanner import AssetManifest


@dataclass
class TaggedAsset:
    path: Path
    category: str
    tags: Set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "category": self.category,
            "tags": sorted(self.tags),
        }


@dataclass
class TaggerResult:
    tagged: List[TaggedAsset] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.tagged)

    def tags_for(self, path: Path) -> Set[str]:
        for asset in self.tagged:
            if asset.path == path:
                return asset.tags
        return set()

    def assets_with_tag(self, tag: str) -> List[TaggedAsset]:
        return [a for a in self.tagged if tag in a.tags]

    def all_tags(self) -> List[str]:
        tags: Set[str] = set()
        for asset in self.tagged:
            tags.update(asset.tags)
        return sorted(tags)


_CATEGORY_TAGS: Dict[str, str] = {
    "images": "visual",
    "audio": "sound",
    "fonts": "typography",
    "data": "data",
    "video": "visual",
}

_SIZE_THRESHOLDS = {
    "large": 500 * 1024,
    "medium": 50 * 1024,
}


def _size_tag(size: int) -> str:
    if size >= _SIZE_THRESHOLDS["large"]:
        return "large"
    if size >= _SIZE_THRESHOLDS["medium"]:
        return "medium"
    return "small"


def tag_assets(manifest: AssetManifest, extra_rules: Dict[str, List[str]] | None = None) -> TaggerResult:
    """Tag every asset in the manifest based on category, size, path, and optional rules."""
    result = TaggerResult()
    rules = extra_rules or {}

    for category, paths in manifest.assets.items():
        for path in paths:
            tags: Set[str] = set()

            # Category-derived tag
            if category in _CATEGORY_TAGS:
                tags.add(_CATEGORY_TAGS[category])
            tags.add(category)

            # Size-derived tag
            try:
                size = path.stat().st_size
                tags.add(_size_tag(size))
            except OSError:
                tags.add("unknown-size")

            # Path-pattern rules: {tag: [substring, ...]}
            for tag, patterns in rules.items():
                if any(pat in str(path) for pat in patterns):
                    tags.add(tag)

            result.tagged.append(TaggedAsset(path=path, category=category, tags=tags))

    return result
