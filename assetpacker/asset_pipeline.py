"""Orchestrates the full asset processing pipeline: scan → filter → optimize → pack → report."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from assetpacker.config import PackerConfig
from assetpacker.scanner import scan_directory, AssetManifest
from assetpacker.filter import FilterConfig, apply_filter
from assetpacker.optimizer import optimize_assets, OptimizeSummary
from assetpacker.packer import pack_to_zip, pack_to_folder, PackResult
from assetpacker.reporter import BuildReport
from assetpacker.logger import BuildLogger
from assetpacker.hooks import HookConfig, run_hooks


@dataclass
class PipelineResult:
    manifest: AssetManifest
    optimize_summary: OptimizeSummary
    pack_result: PackResult
    report: BuildReport
    success: bool
    errors: list = field(default_factory=list)

    def summary(self) -> str:
        status = "OK" if self.success else "FAILED"
        return (
            f"[{status}] {self.manifest.total} assets processed, "
            f"{self.pack_result.files_packed} packed, "
            f"{self.pack_result.bundle_size_kb():.1f} KB output"
        )


def run_pipeline(
    config: PackerConfig,
    source_dir: Path,
    output_dir: Path,
    logger: Optional[BuildLogger] = None,
    filter_config: Optional[FilterConfig] = None,
    hook_config: Optional[HookConfig] = None,
) -> PipelineResult:
    """Execute the full asset pipeline and return a consolidated result."""
    if logger is None:
        logger = BuildLogger()

    errors = []

    logger.info(f"Scanning {source_dir}")
    manifest = scan_directory(source_dir)
    logger.info(f"Found {manifest.total} assets")

    if filter_config is not None:
        manifest = apply_filter(manifest, filter_config)
        logger.info(f"After filter: {manifest.total} assets")

    if hook_config and hook_config.pre_build:
        hook_result = run_hooks(hook_config.pre_build)
        if not hook_result.success:
            errors.extend(hook_result.errors)
            logger.warning(f"Pre-build hooks failed: {hook_result.errors}")

    logger.info("Optimizing assets")
    opt_summary = optimize_assets(manifest, config, output_dir)

    logger.info(f"Packing to {config.target}")
    if config.target == "zip":
        pack_result = pack_to_zip(opt_summary, config, output_dir)
    else:
        pack_result = pack_to_folder(opt_summary, config, output_dir)

    if hook_config and hook_config.post_build:
        hook_result = run_hooks(hook_config.post_build)
        if not hook_result.success:
            errors.extend(hook_result.errors)
            logger.warning(f"Post-build hooks failed: {hook_result.errors}")

    report = BuildReport(optimize_summary=opt_summary, pack_result=pack_result)
    success = len(errors) == 0 and pack_result.files_packed > 0

    logger.info("Pipeline complete")
    return PipelineResult(
        manifest=manifest,
        optimize_summary=opt_summary,
        pack_result=pack_result,
        report=report,
        success=success,
        errors=errors,
    )
