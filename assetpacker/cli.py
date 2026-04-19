"""Command-line entry point for assetpacker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assetpacker.config import load_config
from assetpacker.scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assetpacker",
        description="Bundle and optimize game assets for web and desktop exports.",
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_cmd = subparsers.add_parser("scan", help="Scan a directory and report discovered assets.")
    scan_cmd.add_argument("source", help="Source asset directory to scan.")
    scan_cmd.add_argument(
        "--config", "-c", default=None, metavar="FILE", help="Path to packer config file."
    )
    scan_cmd.add_argument(
        "--exclude", nargs="*", default=[], metavar="NAME", help="Directory/file names to exclude."
    )

    return parser


def cmd_scan(args: argparse.Namespace) -> int:
    config = None
    if args.config:
        try:
            config = load_config(args.config)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    exclude = list(args.exclude)
    if config and hasattr(config, "exclude"):
        exclude = list(set(exclude) | set(config.exclude or []))

    try:
        manifest = scan_directory(args.source, exclude=exclude or None)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = manifest.summary()
    print(f"Scan results for: {Path(args.source).resolve()}")
    print(f"  Images : {summary['images']}")
    print(f"  Audio  : {summary['audio']}")
    print(f"  Fonts  : {summary['fonts']}")
    print(f"  Data   : {summary['data']}")
    print(f"  Unknown: {summary['unknown']}")
    print(f"  Total  : {summary['total']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return cmd_scan(args)

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
