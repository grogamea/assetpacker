"""Tests for assetpacker.pipeline_config — PipelineConfig loading and description."""

import json
import pytest
from pathlib import Path

from assetpacker.pipeline_config import (
    PipelineConfig,
    load_pipeline_config,
    describe_pipeline_config,
)
from assetpacker.config import PackerConfig
from assetpacker.filter import FilterConfig
from assetpacker.hooks import HookConfig


@pytest.fixture
def default_cfg():
    return PipelineConfig(
        packer=PackerConfig(),
        filter=FilterConfig(),
        hooks=HookConfig(pre_build=[], post_build=[]),
    )


def test_default_source_dir(default_cfg):
    assert default_cfg.source_dir == Path("assets")


def test_default_output_dir(default_cfg):
    assert default_cfg.output_dir == Path("dist")


def test_from_dict_sets_source_dir():
    cfg = PipelineConfig.from_dict({"source_dir": "game/assets"})
    assert cfg.source_dir == Path("game/assets")


def test_from_dict_sets_output_dir():
    cfg = PipelineConfig.from_dict({"output_dir": "build/out"})
    assert cfg.output_dir == Path("build/out")


def test_from_dict_empty_uses_defaults():
    cfg = PipelineConfig.from_dict({})
    assert cfg.source_dir == Path("assets")
    assert cfg.output_dir == Path("dist")


def test_to_dict_roundtrip():
    cfg = PipelineConfig.from_dict({"source_dir": "src", "output_dir": "out"})
    d = cfg.to_dict()
    assert d["source_dir"] == "src"
    assert d["output_dir"] == "out"


def test_load_pipeline_config_from_file(tmp_path):
    data = {"source_dir": "game/assets", "output_dir": "game/dist"}
    cfg_file = tmp_path / "pipeline.json"
    cfg_file.write_text(json.dumps(data))
    cfg = load_pipeline_config(cfg_file)
    assert cfg.source_dir == Path("game/assets")
    assert cfg.output_dir == Path("game/dist")


def test_load_pipeline_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_pipeline_config(tmp_path / "nonexistent.json")


def test_describe_pipeline_config_contains_source(default_cfg):
    desc = describe_pipeline_config(default_cfg)
    assert "assets" in desc


def test_describe_pipeline_config_contains_target(default_cfg):
    desc = describe_pipeline_config(default_cfg)
    assert "Target" in desc
