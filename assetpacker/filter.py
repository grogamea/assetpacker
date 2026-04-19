"""Asset filtering utilities for including/excluding files by pattern."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from assetpacker.scanner import AssetManifest


@dataclass
class FilterConfig:
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "FilterConfig":
        return cls(
            include=data.get("include", []),
            exclude=data.get("exclude", []),
        )


def _matches_any(path: Path, patterns: List[str]) -> bool:
    name = path.name
    parts = path.parts
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True
    return False


def apply_filter(manifest: AssetManifest, config: FilterConfig) -> AssetManifest:
    """Return a new AssetManifest with files filtered by include/exclude rules."""
    all_files = manifest.all_assets()

    if config.include:
        all_files = [f for f in all_files if _matches_any(f, config.include)]

    if config.exclude:
        all_files = [f for f in all_files if not _matches_any(f, config.exclude)]

    filtered: dict[str, list[Path]] = {"images": [], "audio": [], "fonts": [], "other": []}
    for f in all_files:
        for category, assets in vars(manifest).items():
            if f in assets:
                filtered[category].append(f)
                break

    from assetpacker.scanner import AssetManifest as AM
    return AM(
        images=filtered["images"],
        audio=filtered["audio"],
        fonts=filtered["fonts"],
        other=filtered["other"],
    )


def describe_filter(config: FilterConfig) -> str:
    parts = []
    if config.include:
        parts.append(f"include={config.include}")
    if config.exclude:
        parts.append(f"exclude={config.exclude}")
    return "FilterConfig(" + ", ".join(parts) + ")" if parts else "FilterConfig(no rules)"
