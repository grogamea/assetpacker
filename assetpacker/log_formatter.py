"""Format BuildLogger output for CLI display and JSON export."""
from __future__ import annotations
from typing import Dict, Any, List
from assetpacker.logger import BuildLogger, LogLevel


ANSI = {
    LogLevel.INFO: "\033[32m",
    LogLevel.WARNING: "\033[33m",
    LogLevel.ERROR: "\033[31m",
    LogLevel.DEBUG: "\033[36m",
}
RESET = "\033[0m"


def format_plain(logger: BuildLogger) -> str:
    """Return plain-text log output."""
    return "\n".join(logger.to_lines())


def format_colored(logger: BuildLogger) -> str:
    """Return ANSI-colored log output for terminal display."""
    lines = []
    for entry in logger.entries:
        color = ANSI.get(entry.level, "")
        lines.append(f"{color}{entry}{RESET}")
    return "\n".join(lines)


def format_json(logger: BuildLogger) -> List[Dict[str, Any]]:
    """Return log entries as a list of dicts for JSON serialization."""
    return [
        {
            "level": entry.level.value,
            "message": entry.message,
            "timestamp": entry.timestamp,
        }
        for entry in logger.entries
    ]


def summary_line(logger: BuildLogger) -> str:
    """Return a one-line summary of log counts by level."""
    counts: Dict[str, int] = {}
    for entry in logger.entries:
        counts[entry.level.value] = counts.get(entry.level.value, 0) + 1
    parts = [f"{v} {k.lower()}(s)" for k, v in counts.items()]
    return "Log summary: " + ", ".join(parts) if parts else "Log summary: no entries"
