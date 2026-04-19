"""Tests for assetpacker configuration loading and validation."""

import json
import os
import pytest
from unittest.mock import patch

from assetpacker.config import PackerConfig, load_config


def test_default_config():
    cfg = PackerConfig()
    assert cfg.input_dir == "assets"
    assert cfg.output_dir == "dist"
    assert cfg.target == "web"
    assert cfg.image_quality == 85
    assert cfg.compress_audio is True


def test_load_config_missing_file():
    cfg = load_config("nonexistent_config.json")
    assert isinstance(cfg, PackerConfig)
    assert cfg.input_dir == "assets"


def test_load_config_from_file(tmp_path):
    config_data = {
        "input_dir": str(tmp_path / "assets"),
        "output_dir": "build",
        "target": "desktop",
        "image_quality": 90,
    }
    config_file = tmp_path / "assetpacker.json"
    config_file.write_text(json.dumps(config_data))

    cfg = load_config(str(config_file))
    assert cfg.output_dir == "build"
    assert cfg.target == "desktop"
    assert cfg.image_quality == 90


def test_load_config_unknown_key(tmp_path):
    config_file = tmp_path / "assetpacker.json"
    config_file.write_text(json.dumps({"unknown_key": "value"}))
    with pytest.raises(ValueError, match="Unknown config keys"):
        load_config(str(config_file))


def test_validate_invalid_target(tmp_path):
    cfg = PackerConfig(input_dir=str(tmp_path), target="mobile")
    with pytest.raises(ValueError, match="target must be"):
        cfg.validate()


def test_validate_invalid_quality(tmp_path):
    cfg = PackerConfig(input_dir=str(tmp_path), image_quality=0)
    with pytest.raises(ValueError, match="image_quality"):
        cfg.validate()


def test_validate_missing_input_dir():
    cfg = PackerConfig(input_dir="/nonexistent/path/xyz")
    with pytest.raises(ValueError, match="input_dir"):
        cfg.validate()


def test_validate_success(tmp_path):
    cfg = PackerConfig(input_dir=str(tmp_path), target="web", image_quality=75)
    cfg.validate()  # should not raise
