"""Sort and prioritize assets for packing order."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

from assetpacker.scanner import AssetManifest

PRIORITY_ORDER = {
    "fonts": 0,
    "images": 1,
    "audio": 2,
    "other": 3,
}


@dataclass
class SortedManifest:
    assets: List[Path] = field(default_factory=list)
    order_map: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.assets)

    def position_of(self, path: Path) -> Optional[int]:
        return self.order_map.get(str(path))


def _category_for(path: Path, manifest: AssetManifest) -> str:
    for category, assets in [
        ("images", manifest.images),
        ("audio", manifest.audio),
        ("fonts", manifest.fonts),
    ]:
        if path in assets:
            return category
    return "other"


def sort_assets(
    manifest: AssetManifest,
    reverse: bool = False,
    by_size: bool = False,
) -> SortedManifest:
    """Return a SortedManifest with assets ordered by category priority.

    If by_size is True, assets within each category are sorted by file size
    (ascending). If reverse is True, the overall order is reversed.
    """
    all_paths = manifest.all_assets()

    def sort_key(p: Path):
        cat = _category_for(p, manifest)
        priority = PRIORITY_ORDER.get(cat, 99)
        size = p.stat().st_size if by_size and p.exists() else 0
        return (priority, size, p.name)

    sorted_paths = sorted(all_paths, key=sort_key, reverse=reverse)

    order_map = {str(p): idx for idx, p in enumerate(sorted_paths)}
    return SortedManifest(assets=sorted_paths, order_map=order_map)


def describe_sort(sorted_manifest: SortedManifest, manifest: AssetManifest) -> str:
    """Return a human-readable summary of the sort order."""
    lines = [f"Sorted {sorted_manifest.total} asset(s):"] 
    for cat in ("fonts", "images", "audio", "other"):
        if cat == "fonts":
            items = manifest.fonts
        elif cat == "images":
            items = manifest.images
        elif cat == "audio":
            items = manifest.audio
        else:
            items = manifest.other
        if items:
            lines.append(f"  {cat}: {len(items)} file(s)")
    return "\n".join(lines)
