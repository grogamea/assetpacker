"""Write asset manifests to disk in various formats."""
from __future__ import annotations
import json
import csv
import io
from pathlib import Path
from typing import Literal

from assetpacker.scanner import AssetManifest

OutputFormat = Literal["json", "csv", "txt"]


def write_manifest(manifest: AssetManifest, dest: Path, fmt: OutputFormat = "json") -> Path:
    """Write manifest to *dest* and return the written path."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        return _write_json(manifest, dest)
    elif fmt == "csv":
        return _write_csv(manifest, dest)
    elif fmt == "txt":
        return _write_txt(manifest, dest)
    else:
        raise ValueError(f"Unknown format: {fmt!r}")


def _write_json(manifest: AssetManifest, dest: Path) -> Path:
    data = {
        "total": len(manifest.all_assets()),
        "categories": {
            cat: [str(p) for p in paths]
            for cat, paths in {
                "images": manifest.images,
                "audio": manifest.audio,
                "fonts": manifest.fonts,
                "data": manifest.data,
                "other": manifest.other,
            }.items()
        },
    }
    dest.write_text(json.dumps(data, indent=2))
    return dest


def _write_csv(manifest: AssetManifest, dest: Path) -> Path:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["category", "path"])
    for cat, paths in [
        ("images", manifest.images),
        ("audio", manifest.audio),
        ("fonts", manifest.fonts),
        ("data", manifest.data),
        ("other", manifest.other),
    ]:
        for p in paths:
            writer.writerow([cat, str(p)])
    dest.write_text(buf.getvalue())
    return dest


def _write_txt(manifest: AssetManifest, dest: Path) -> Path:
    lines = [f"# Asset Manifest — {len(manifest.all_assets())} files\n"]
    for cat, paths in [
        ("images", manifest.images),
        ("audio", manifest.audio),
        ("fonts", manifest.fonts),
        ("data", manifest.data),
        ("other", manifest.other),
    ]:
        if paths:
            lines.append(f"[{cat}]")
            lines.extend(f"  {p}" for p in paths)
    dest.write_text("\n".join(lines))
    return dest
