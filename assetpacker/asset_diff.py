"""Compute diffs between two asset manifests to detect added, removed, and changed assets."""

from dataclasses import dataclass, field
from typing import List, Dict
from assetpacker.scanner import AssetManifest


@dataclass
class DiffResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)

    @property
    def has_changes(self) -> bool:
        return self.total_changes > 0

    def to_dict(self) -> Dict:
        return {
            "added": sorted(self.added),
            "removed": sorted(self.removed),
            "changed": sorted(self.changed),
            "total_changes": self.total_changes,
        }

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


def diff_manifests(old: AssetManifest, new: AssetManifest) -> DiffResult:
    """Compare two AssetManifests and return a DiffResult describing changes."""
    old_map: Dict[str, float] = {str(p): p.stat().st_mtime for p in old.all_assets()}
    new_map: Dict[str, float] = {str(p): p.stat().st_mtime for p in new.all_assets()}

    old_keys = set(old_map)
    new_keys = set(new_map)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(
        key for key in old_keys & new_keys if old_map[key] != new_map[key]
    )

    return DiffResult(added=added, removed=removed, changed=changed)


def describe_diff(result: DiffResult) -> str:
    """Return a human-readable multi-line description of a DiffResult."""
    if not result.has_changes:
        return "No changes detected between manifests."

    lines = [f"Manifest diff: {result.summary()}"]
    for path in result.added:
        lines.append(f"  + {path}")
    for path in result.removed:
        lines.append(f"  - {path}")
    for path in result.changed:
        lines.append(f"  ~ {path}")
    return "\n".join(lines)
