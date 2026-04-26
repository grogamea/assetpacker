"""CLI-facing entry point that loads PipelineConfig and executes run_pipeline."""

from pathlib import Path
from typing import Optional

from assetpacker.pipeline_config import PipelineConfig, load_pipeline_config, describe_pipeline_config
from assetpacker.asset_pipeline import run_pipeline, PipelineResult
from assetpacker.logger import BuildLogger
from assetpacker.stats import compute_stats
from assetpacker.stats_renderer import render_text


def execute(
    config_path: Optional[Path] = None,
    source_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    verbose: bool = False,
) -> PipelineResult:
    """Load config and run the full pipeline. Returns PipelineResult."""
    logger = BuildLogger()

    if config_path and config_path.exists():
        cfg = load_pipeline_config(config_path)
        logger.info(f"Loaded pipeline config from {config_path}")
    else:
        from assetpacker.config import PackerConfig
        from assetpacker.filter import FilterConfig
        from assetpacker.hooks import HookConfig
        cfg = PipelineConfig(
            packer=PackerConfig(),
            filter=FilterConfig(),
            hooks=HookConfig(pre_build=[], post_build=[]),
        )
        logger.info("Using default pipeline config")

    if source_dir:
        cfg.source_dir = source_dir
    if output_dir:
        cfg.output_dir = output_dir

    if verbose:
        logger.debug("Pipeline configuration:\n" + describe_pipeline_config(cfg))

    result = run_pipeline(
        config=cfg.packer,
        source_dir=cfg.source_dir,
        output_dir=cfg.output_dir,
        logger=logger,
        filter_config=cfg.filter,
        hook_config=cfg.hooks,
    )

    stats = compute_stats(result.optimize_summary, result.pack_result)
    if verbose:
        print(render_text(stats))

    logger.info(result.summary())
    return result


def execute_from_dict(data: dict, verbose: bool = False) -> PipelineResult:
    """Run the pipeline from a config dictionary (useful for programmatic use)."""
    cfg = PipelineConfig.from_dict(data)
    logger = BuildLogger()
    result = run_pipeline(
        config=cfg.packer,
        source_dir=cfg.source_dir,
        output_dir=cfg.output_dir,
        logger=logger,
        filter_config=cfg.filter,
        hook_config=cfg.hooks,
    )
    return result
