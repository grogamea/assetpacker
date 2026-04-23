"""Catalog exporter: serializes an AssetCatalog to JSON, CSV, or Markdown."""

import csv
import json
from pathlib import Path
from typing import Literal

from assetpacker.asset_catalog import AssetCatalog

ExportFormat = Literal["json", "csv", "markdown"]


def export_catalog(catalog: AssetCatalog, dest: Path, fmt: ExportFormat = "json") -> Path:
    """Export catalog to *dest* in the requested format. Returns the output path."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        return _export_json(catalog, dest)
    elif fmt == "csv":
        return _export_csv(catalog, dest)
    elif fmt == "markdown":
        return _export_markdown(catalog, dest)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")


def _export_json(catalog: AssetCatalog, dest: Path) -> Path:
    dest.write_text(json.dumps(catalog.to_dict(), indent=2), encoding="utf-8")
    return dest


def _export_csv(catalog: AssetCatalog, dest: Path) -> Path:
    with dest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["path", "category", "size_bytes", "stem", "suffix"]
        )
        writer.writeheader()
        for entry in catalog.entries:
            writer.writerow(entry.to_dict())
    return dest


def _export_markdown(catalog: AssetCatalog, dest: Path) -> Path:
    lines = [
        "# Asset Catalog\n",
        f"**Total assets:** {catalog.total}  ",
        f"**Categories:** {', '.join(catalog.categories())}\n",
        "| Path | Category | Size (bytes) | Suffix |",
        "|------|----------|-------------|--------|\n",
    ]
    for entry in sorted(catalog.entries, key=lambda e: (e.category, str(e.path))):
        lines.append(
            f"| {entry.path} | {entry.category} | {entry.size_bytes} | {entry.suffix} |"
        )
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def describe_export(catalog: AssetCatalog, fmt: ExportFormat) -> str:
    """Return a human-readable summary of what would be exported."""
    return (
        f"Exporting {catalog.total} assets across "
        f"{len(catalog.categories())} categories as {fmt.upper()}."
    )
