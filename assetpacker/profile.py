"""Build profiles for preset configurations (web, desktop, mobile)."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

BUILTIN_PROFILES: Dict[str, Dict[str, Any]] = {
    "web": {
        "target": "web",
        "image_quality": 80,
        "audio_bitrate": 128,
        "compress": True,
        "pack_format": "zip",
    },
    "desktop": {
        "target": "desktop",
        "image_quality": 95,
        "audio_bitrate": 320,
        "compress": False,
        "pack_format": "folder",
    },
    "mobile": {
        "target": "mobile",
        "image_quality": 65,
        "audio_bitrate": 96,
        "compress": True,
        "pack_format": "zip",
    },
}


@dataclass
class BuildProfile:
    name: str
    target: str
    image_quality: int
    audio_bitrate: int
    compress: bool
    pack_format: str
    overrides: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "target": self.target,
            "image_quality": self.image_quality,
            "audio_bitrate": self.audio_bitrate,
            "compress": self.compress,
            "pack_format": self.pack_format,
        }
        base.update(self.overrides)
        return base


def load_profile(name: str, overrides: Optional[Dict[str, Any]] = None) -> BuildProfile:
    if name not in BUILTIN_PROFILES:
        raise ValueError(f"Unknown profile '{name}'. Available: {list(BUILTIN_PROFILES)}")
    data = dict(BUILTIN_PROFILES[name])
    return BuildProfile(
        name=name,
        target=data["target"],
        image_quality=data["image_quality"],
        audio_bitrate=data["audio_bitrate"],
        compress=data["compress"],
        pack_format=data["pack_format"],
        overrides=overrides or {},
    )


def list_profiles() -> list:
    return list(BUILTIN_PROFILES.keys())
