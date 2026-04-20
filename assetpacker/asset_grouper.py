"""Groups assets by configurable criteria such as category, extension, or tag prefix."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from assetpacker.scanner import AssetManifest


@dataclass
class AssetGroup:
    name: str
    assets: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.assets)

    def to_dict(self) -> dict:
        return {"name": self.name, "count": self.count, "assets": self.assets}


@dataclass
class GroupResult:
    groups: Dict[str, AssetGroup] = field(default_factory=dict)

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_assets(self) -> int:
        return sum(g.count for g in self.groups.values())

    def get(self, name: str) -> Optional[AssetGroup]:
        return self.groups.get(name)

    def to_dict(self) -> dict:
        return {name: group.to_dict() for name, group in self.groups.items()}


def group_by_category(manifest: AssetManifest) -> GroupResult:
    """Group assets by their scanner category (images, audio, fonts, etc.)."""
    result = GroupResult()
    for category, assets in manifest.categories.items():
        group = AssetGroup(name=category, assets=list(assets))
        result.groups[category] = group
    return result


def group_by_extension(manifest: AssetManifest) -> GroupResult:
    """Group assets by file extension."""
    result = GroupResult()
    for asset in manifest.all_assets():
        ext = asset.rsplit(".", 1)[-1].lower() if "." in asset else "no_ext"
        if ext not in result.groups:
            result.groups[ext] = AssetGroup(name=ext)
        result.groups[ext].assets.append(asset)
    return result


def group_by_prefix(manifest: AssetManifest, separator: str = "/") -> GroupResult:
    """Group assets by their top-level directory prefix."""
    result = GroupResult()
    for asset in manifest.all_assets():
        parts = asset.split(separator)
        prefix = parts[0] if len(parts) > 1 else "_root"
        if prefix not in result.groups:
            result.groups[prefix] = AssetGroup(name=prefix)
        result.groups[prefix].assets.append(asset)
    return result


def describe_groups(result: GroupResult) -> str:
    """Return a human-readable summary of a GroupResult."""
    lines = [f"Groups ({len(result.groups)} total, {result.total_assets} assets):"]
    for name in result.group_names:
        group = result.groups[name]
        lines.append(f"  [{name}] {group.count} asset(s)")
    return "\n".join(lines)
