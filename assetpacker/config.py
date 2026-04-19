"""Configuration loading and validation for assetpacker."""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PackerConfig:
    input_dir: str = "assets"
    output_dir: str = "dist"
    formats: List[str] = field(default_factory=lambda: ["png", "jpg", "ogg", "wav"])
    image_quality: int = 85
    compress_audio: bool = True
    target: str = "web"  # web | desktop
    exclude_patterns: List[str] = field(default_factory=list)
    max_texture_size: Optional[int] = None

    def validate(self):
        errors = []
        if not os.path.isdir(self.input_dir):
            errors.append(f"input_dir '{self.input_dir}' does not exist or is not a directory")
        if self.target not in ("web", "desktop"):
            errors.append(f"target must be 'web' or 'desktop', got '{self.target}'")
        if not (1 <= self.image_quality <= 100):
            errors.append(f"image_quality must be between 1 and 100, got {self.image_quality}")
        if self.max_texture_size is not None and self.max_texture_size <= 0:
            errors.append(f"max_texture_size must be a positive integer")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


def load_config(path: str = "assetpacker.json") -> PackerConfig:
    """Load configuration from a JSON file, falling back to defaults."""
    if not os.path.exists(path):
        return PackerConfig()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    allowed = PackerConfig.__dataclass_fields__.keys()
    unknown = set(data) - set(allowed)
    if unknown:
        raise ValueError(f"Unknown config keys: {', '.join(sorted(unknown))}")

    return PackerConfig(**{k: v for k, v in data.items() if k in allowed})
