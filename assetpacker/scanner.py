"""Asset scanner: discovers and categorizes asset files from a source directory."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tga"}
AUDIO_EXTENSIONS = {".wav", ".ogg", ".mp3", ".flac", ".aiff"}
FONT_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}
DATA_EXTENSIONS = {".json", ".xml", ".csv", ".yaml", ".yml"}


@dataclass
class AssetManifest:
    images: List[Path] = field(default_factory=list)
    audio: List[Path] = field(default_factory=list)
    fonts: List[Path] = field(default_factory=list)
    data: List[Path] = field(default_factory=list)
    unknown: List[Path] = field(default_factory=list)

    def all_assets(self) -> List[Path]:
        return self.images + self.audio + self.fonts + self.data + self.unknown

    def summary(self) -> Dict[str, int]:
        return {
            "images": len(self.images),
            "audio": len(self.audio),
            "fonts": len(self.fonts),
            "data": len(self.data),
            "unknown": len(self.unknown),
            "total": len(self.all_assets()),
        }


def scan_directory(source_dir: str | Path, exclude: list[str] | None = None) -> AssetManifest:
    """Recursively scan *source_dir* and return a categorized AssetManifest.

    Args:
        source_dir: Root directory to scan.
        exclude: List of glob-style directory or file names to skip.
    """
    source_dir = Path(source_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {source_dir}")

    exclude_set = set(exclude or [])
    manifest = AssetManifest()

    for root, dirs, files in os.walk(source_dir):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_set]

        for filename in files:
            if filename in exclude_set:
                continue
            path = Path(root) / filename
            ext = path.suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                manifest.images.append(path)
            elif ext in AUDIO_EXTENSIONS:
                manifest.audio.append(path)
            elif ext in FONT_EXTENSIONS:
                manifest.fonts.append(path)
            elif ext in DATA_EXTENSIONS:
                manifest.data.append(path)
            else:
                manifest.unknown.append(path)

    return manifest
