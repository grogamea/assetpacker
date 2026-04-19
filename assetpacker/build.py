"""Orchestrates a full asset build: scan → optimize → pack, with cache support."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from assetpacker.cache import BuildCache
from assetpacker.config import PackerConfig
from assetpacker.scanner import scan_directory
from assetpacker.optimizer import optimize_assets
from assetpacker.packer import pack_to_zip, pack_to_folder
from assetpacker.reporter import BuildReport


@dataclass
class BuildContext:
    config: PackerConfig
    source_dir: Path
    output_dir: Path
    cache_file: Path
    force: bool = False


def run_build(ctx: BuildContext) -> BuildReport:
    """Execute a full build and return a BuildReport."""
    cache = BuildCache() if ctx.force else BuildCache.load(ctx.cache_file)

    manifest = scan_directory(ctx.source_dir)

    changed = [
        a for a in manifest.all_assets()
        if ctx.force or cache.is_changed(Path(a))
    ]

    optimize_summary = optimize_assets(
        manifest=manifest,
        config=ctx.config,
        output_dir=ctx.output_dir,
        only_paths=set(changed) if not ctx.force else None,
    )

    if ctx.config.target == "web":
        pack_result = pack_to_zip(
            optimize_summary, ctx.config, ctx.output_dir
        )
    else:
        pack_result = pack_to_folder(
            optimize_summary, ctx.config, ctx.output_dir
        )

    for path_str in changed:
        p = Path(path_str)
        if p.exists():
            cache.update(p)

    cache.save(ctx.cache_file)

    return BuildReport(
        optimize_summary=optimize_summary,
        pack_result=pack_result,
        output_path=str(ctx.output_dir),
    )
