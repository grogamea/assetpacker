"""Merge a BuildProfile into a PackerConfig, with config values taking precedence."""
from typing import Any, Dict
from assetpacker.profile import BuildProfile
from assetpacker.config import PackerConfig


MERGEABLE_KEYS = ("target", "image_quality", "audio_bitrate", "compress", "pack_format")


def merge_profile_into_config(profile: BuildProfile, config: PackerConfig) -> PackerConfig:
    """Return a new PackerConfig with profile defaults filled in where config has None."""
    profile_data = profile.to_dict()
    merged: Dict[str, Any] = {}

    for key in MERGEABLE_KEYS:
        config_val = getattr(config, key, None)
        if config_val is None:
            merged[key] = profile_data.get(key)
        else:
            merged[key] = config_val

    # Preserve non-mergeable config fields
    for attr in vars(config):
        if attr not in merged:
            merged[attr] = getattr(config, attr)

    return PackerConfig(**{k: v for k, v in merged.items() if k in PackerConfig.__dataclass_fields__})


def describe_merge(profile: BuildProfile, config: PackerConfig) -> Dict[str, str]:
    """Return a dict describing which source each key came from."""
    profile_data = profile.to_dict()
    sources: Dict[str, str] = {}
    for key in MERGEABLE_KEYS:
        config_val = getattr(config, key, None)
        if config_val is None:
            sources[key] = f"profile:{profile.name}"
        else:
            sources[key] = "config"
    return sources
