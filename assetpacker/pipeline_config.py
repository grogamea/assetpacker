"""Pipeline-level configuration: combines PackerConfig, FilterConfig, and HookConfig."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from assetpacker.config import PackerConfig, load_config
from assetpacker.filter import FilterConfig
from assetpacker.hooks import HookConfig


@dataclass
class PipelineConfig:
    packer: PackerConfig
    filter: FilterConfig = field(default_factory=FilterConfig)
    hooks: HookConfig = field(default_factory=lambda: HookConfig(pre_build=[], post_build=[]))
    source_dir: Path = Path("assets")
    output_dir: Path = Path("dist")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineConfig":
        packer_data = data.get("packer", {})
        filter_data = data.get("filter", {})
        hooks_data = data.get("hooks", {})
        return cls(
            packer=PackerConfig(**packer_data) if packer_data else PackerConfig(),
            filter=FilterConfig.from_dict(filter_data),
            hooks=HookConfig.from_dict(hooks_data) if hasattr(HookConfig, "from_dict") else HookConfig(**hooks_data),
            source_dir=Path(data.get("source_dir", "assets")),
            output_dir=Path(data.get("output_dir", "dist")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "packer": vars(self.packer),
            "filter": vars(self.filter),
            "hooks": {"pre_build": self.hooks.pre_build, "post_build": self.hooks.post_build},
            "source_dir": str(self.source_dir),
            "output_dir": str(self.output_dir),
        }


def load_pipeline_config(path: Path) -> PipelineConfig:
    """Load a PipelineConfig from a TOML/JSON config file."""
    import json

    if not path.exists():
        raise FileNotFoundError(f"Pipeline config not found: {path}")

    with open(path) as f:
        data = json.load(f)

    return PipelineConfig.from_dict(data)


def describe_pipeline_config(cfg: PipelineConfig) -> str:
    lines = [
        f"Source : {cfg.source_dir}",
        f"Output : {cfg.output_dir}",
        f"Target : {cfg.packer.target}",
        f"Compress: {cfg.packer.compress}",
        f"Filter includes: {cfg.filter.include or ['*']}",
        f"Filter excludes: {cfg.filter.exclude or []}",
        f"Pre-build hooks : {len(cfg.hooks.pre_build)}",
        f"Post-build hooks: {len(cfg.hooks.post_build)}",
    ]
    return "\n".join(lines)
