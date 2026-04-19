"""Tests for build profile loading and resolution."""
import pytest
from assetpacker.profile import (
    BuildProfile,
    load_profile,
    list_profiles,
    BUILTIN_PROFILES,
)


def test_list_profiles_returns_all_builtins():
    profiles = list_profiles()
    assert "web" in profiles
    assert "desktop" in profiles
    assert "mobile" in profiles


def test_load_web_profile():
    p = load_profile("web")
    assert p.name == "web"
    assert p.target == "web"
    assert p.pack_format == "zip"
    assert p.compress is True


def test_load_desktop_profile():
    p = load_profile("desktop")
    assert p.target == "desktop"
    assert p.compress is False
    assert p.pack_format == "folder"
    assert p.image_quality == 95


def test_load_mobile_profile():
    p = load_profile("mobile")
    assert p.audio_bitrate == 96
    assert p.image_quality == 65


def test_load_unknown_profile_raises():
    with pytest.raises(ValueError, match="Unknown profile"):
        load_profile("nonexistent")


def test_overrides_applied_to_dict():
    p = load_profile("web", overrides={"image_quality": 50})
    d = p.to_dict()
    assert d["image_quality"] == 50


def test_overrides_do_not_mutate_builtin():
    load_profile("web", overrides={"image_quality": 10})
    assert BUILTIN_PROFILES["web"]["image_quality"] == 80


def test_to_dict_contains_all_keys():
    p = load_profile("desktop")
    d = p.to_dict()
    for key in ("target", "image_quality", "audio_bitrate", "compress", "pack_format"):
        assert key in d


def test_profile_name_preserved():
    p = load_profile("mobile")
    assert p.name == "mobile"
