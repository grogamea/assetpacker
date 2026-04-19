"""CLI entry point for assetpacker."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assetpacker.config import load_config
from assetpacker.scanner import scan_directory
from assetpacker.optimizer import optimize
from assetpacker.packer import pack
from assetpacker.reporter import BuildReport
from assetpacker.watcher import watch, WatchEvent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assetpacker",
        description="Bundle and optimize game assets.",
    )
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="Scan asset directory")
    scan_p.add_argument("path", type=Path)

    build_p = sub.add_parser("build", help="Build asset bundle")
    build_p.add_argument("--config", type=Path, default=Path("assetpacker.toml"))

    watch_p = sub.add_parser("watch", help="Watch for changes and rebuild")
    watch_p.add_argument("path", type=Path)
    watch_p.add_argument("--config", type=Path, default=Path("assetpacker.toml"))
    watch_p.add_argument("--interval", type=float, default=1.0)

    return parser


def cmd_scan(args: argparse.Namespace) -> None:
    manifest = scan_directory(args.path)
    print(manifest.summary())


def cmd_build(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    manifest = scan_directory(Path(config.source_dir))
    opt_summary = optimize(manifest, config)
    result = pack(opt_summary, config)
    report = BuildReport(opt_summary, result)
    print(report.to_json())


def cmd_watch(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    print(f"Watching {args.path} every {args.interval}s …")

    def on_change(events: list[WatchEvent]) -> None:
        for e in events:
            print(f"  {e}")
        print("Rebuilding …")
        manifest = scan_directory(args.path)
        opt_summary = optimize(manifest, config)
        result = pack(opt_summary, config)
        report = BuildReport(opt_summary, result)
        print(report.to_json())

    try:
        watch(args.path, on_change, interval=args.interval)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "watch":
        cmd_watch(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
