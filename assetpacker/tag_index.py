"""Tag-based asset indexing for filtering and grouping assets by user-defined tags."""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from assetpacker.scanner import AssetManifest


@dataclass
class TagIndex:
    _index: Dict[str, Set[str]] = field(default_factory=dict)  # tag -> set of paths
    _asset_tags: Dict[str, Set[str]] = field(default_factory=dict)  # path -> set of tags

    def add(self, path: str, tags: List[str]) -> None:
        """Associate tags with an asset path."""
        self._asset_tags.setdefault(path, set()).update(tags)
        for tag in tags:
            self._index.setdefault(tag, set()).add(path)

    def tags_for(self, path: str) -> Set[str]:
        return set(self._asset_tags.get(path, set()))

    def assets_for_tag(self, tag: str) -> Set[str]:
        return set(self._index.get(tag, set()))

    def all_tags(self) -> List[str]:
        return sorted(self._index.keys())

    def remove(self, path: str) -> None:
        for tag in self._asset_tags.pop(path, set()):
            self._index.get(tag, set()).discard(path)
            if not self._index.get(tag):
                self._index.pop(tag, None)

    def to_dict(self) -> Dict[str, List[str]]:
        return {tag: sorted(paths) for tag, paths in self._index.items()}


def build_tag_index(manifest: AssetManifest, tag_map: Dict[str, List[str]]) -> TagIndex:
    """Build a TagIndex from a manifest and a mapping of path -> tags."""
    index = TagIndex()
    all_paths = manifest.all_assets()
    for path in all_paths:
        tags = tag_map.get(path, [])
        if tags:
            index.add(path, tags)
    return index
