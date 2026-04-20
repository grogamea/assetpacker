"""High-level pipeline that combines scanning, sorting, and reporting."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from assetpacker.scanner import scan_directory, AssetManifest
from assetpacker.asset_sorter import sort_assets, describe_sort, SortedManifest
from assetpacker.logger import BuildLogger


@dataclass
class SortPipelineResult:
    manifest: AssetManifest
    sorted_manifest: SortedManifest
    description: str
    success: bool = True
    error: Optional[str] = None


def run_sort_pipeline(
    root: Path,
    reverse: bool = False,
    by_size: bool = False,
    logger: Optional[BuildLogger] = None,
) -> SortPipelineResult:
    """Scan *root*, sort the discovered assets, and return a pipeline result.

    Parameters
    ----------
    root:     Directory to scan for assets.
    reverse:  Reverse the final sort order.
    by_size:  Sort within each category by ascending file size.
    logger:   Optional BuildLogger for progress messages.
    """
    if logger:
        logger.info(f"sort_pipeline: scanning {root}")

    try:
        manifest = scan_directory(root)
    except Exception as exc:  # pragma: no cover
        msg = f"scan failed: {exc}"
        if logger:
            logger.error(msg)
        return SortPipelineResult(
            manifest=AssetManifest(),
            sorted_manifest=SortedManifest(),
            description="",
            success=False,
            error=msg,
        )

    if logger:
        logger.info(f"sort_pipeline: found {manifest.all_assets().__len__()} asset(s)")

    sorted_manifest = sort_assets(manifest, reverse=reverse, by_size=by_size)
    description = describe_sort(sorted_manifest, manifest)

    if logger:
        logger.info(f"sort_pipeline: sorted {sorted_manifest.total} asset(s)")
        for line in description.splitlines()[1:]:
            logger.debug(line.strip())

    return SortPipelineResult(
        manifest=manifest,
        sorted_manifest=sorted_manifest,
        description=description,
        success=True,
    )
