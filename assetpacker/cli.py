"""CLI entry point for assetpacker."""

import argparse
import sys

from assetpacker.config import load_config
from assetpacker.optimizer import optimize
from assetpacker.packer import pack
from assetpacker.scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assetpacker",
        description="Bundle and optimize game assets for web and desktop exports.",
    )
    parser.add_argument("--config", default="assetpacker.toml", help="Path to config file")
    subparsers = parser.add_subparsers(dest="command")

    scan_p = subparsers.add_parser("scan", help="Scan asset directory and print manifest")
    scan_p.add_argument("directory", help="Directory to scan")

    build_p = subparsers.add_parser("build", help="Optimize and pack assets")
    build_p.add_argument("directory", help="Directory to scan")
    build_p.add_argument(
        "--format", choices=["zip", "folder"], default="zip",
        help="Output bundle format"
    )
    return parser


def cmd_scan(args) -> int:
    manifest = scan_directory(args.directory)
    print(manifest.summary())
    return 0


def cmd_build(args) -> int:
    config = load_config(args.config)
    config.bundle_format = args.format
    manifest = scan_directory(args.directory)
    print(f"Scanned {len(manifest.all_assets())} assets.")
    summary = optimize(manifest, config)
    print(f"Optimized {len(summary.results)} assets — "
          f"saved {summary.total_savings_bytes} bytes.")
    result = pack(summary, config)
    if not result.success:
        for err in result.errors:
            print(f"[error] {err}", file=sys.stderr)
        return 1
    print(f"Packed {result.files_packed} files → {result.output_path} "
          f"({result.bundle_size_kb:.1f} KB)")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scan":
        sys.exit(cmd_scan(args))
    elif args.command == "build":
        sys.exit(cmd_build(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
