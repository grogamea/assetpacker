"""Tests for profile + config merging logic."""
import pytest
from assetpacker.profile import load_profile
from assetpacker.config import PackerConfig
from assetpacker.profile_merger import merge_profile_into_config, describe_merge


@pytest.fixture
def web_profile():
    return load_profile("web")


@pytest.fixture
def empty_config():
    return PackerConfig()


@pytest.fixture
def partial_config():
    return PackerConfig(image_quality=99)


def test_merge_fills_target_from_profile(web_profile, empty_config):
    result = merge_profile_into_config(web_profile, empty_config)
    assert result.target == "web"


def test_merge_fills_compress_from_profile(web_profile, empty_config):
    result = merge_profile_into_config(web_profile, empty_config)
    assert result.compress is True


def test_config_value_takes_precedence(web_profile, partial_config):
    result = merge_profile_into_config(web_profile, partial_config)
    assert result.image_quality == 99


def test_profile_fills_missing_image_quality(web_profile, empty_config):
    result = merge_profile_into_config(web_profile, empty_config)
    assert result.image_quality == 80


def test_describe_merge_config_source(web_profile, partial_config):
    sources = describe_merge(web_profile, partial_config)
    assert sources["image_quality"] == "config"


def test_describe_merge_profile_source(web_profile, empty_config):
    sources = describe_merge(web_profile, empty_config)
    assert sources["target"] == "profile:web"
    assert sources["compress"] == "profile:web"


def test_merge_desktop_profile(empty_config):
    profile = load_profile("desktop")
    result = merge_profile_into_config(profile, empty_config)
    assert result.pack_format == "folder"
    assert result.compress is False


def test_describe_merge_returns_all_config_keys(web_profile, empty_config):
    """Ensure describe_merge covers every key present in the merged result."""
    result = merge_profile_into_config(web_profile, empty_config)
    sources = describe_merge(web_profile, empty_config)
    for key in vars(result):
        assert key in sources, f"describe_merge is missing key: {key!r}"
