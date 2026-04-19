"""Structured build logging for assetpacker."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


@dataclass
class LogEntry:
    level: LogLevel
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level.value}: {self.message}"


@dataclass
class BuildLogger:
    entries: List[LogEntry] = field(default_factory=list)

    def _log(self, level: LogLevel, message: str) -> None:
        self.entries.append(LogEntry(level=level, message=message))

    def info(self, message: str) -> None:
        self._log(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        self._log(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        self._log(LogLevel.ERROR, message)

    def debug(self, message: str) -> None:
        self._log(LogLevel.DEBUG, message)

    def errors(self) -> List[LogEntry]:
        return [e for e in self.entries if e.level == LogLevel.ERROR]

    def warnings(self) -> List[LogEntry]:
        return [e for e in self.entries if e.level == LogLevel.WARNING]

    def has_errors(self) -> bool:
        return len(self.errors()) > 0

    def to_lines(self) -> List[str]:
        return [str(e) for e in self.entries]

    def clear(self) -> None:
        self.entries.clear()
