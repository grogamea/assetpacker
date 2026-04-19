"""Tests for assetpacker.logger."""
import pytest
from assetpacker.logger import BuildLogger, LogLevel, LogEntry


@pytest.fixture
def logger() -> BuildLogger:
    return BuildLogger()


def test_info_adds_entry(logger):
    logger.info("started")
    assert len(logger.entries) == 1
    assert logger.entries[0].level == LogLevel.INFO
    assert logger.entries[0].message == "started"


def test_warning_adds_entry(logger):
    logger.warning("slow asset")
    assert logger.entries[0].level == LogLevel.WARNING


def test_error_adds_entry(logger):
    logger.error("file missing")
    assert logger.entries[0].level == LogLevel.ERROR


def test_debug_adds_entry(logger):
    logger.debug("scanning dir")
    assert logger.entries[0].level == LogLevel.DEBUG


def test_has_errors_false_when_no_errors(logger):
    logger.info("ok")
    assert not logger.has_errors()


def test_has_errors_true_when_error_logged(logger):
    logger.error("boom")
    assert logger.has_errors()


def test_errors_filters_only_errors(logger):
    logger.info("a")
    logger.error("b")
    logger.warning("c")
    assert len(logger.errors()) == 1
    assert logger.errors()[0].message == "b"


def test_warnings_filters_only_warnings(logger):
    logger.warning("w1")
    logger.error("e1")
    assert len(logger.warnings()) == 1


def test_to_lines_returns_strings(logger):
    logger.info("hello")
    lines = logger.to_lines()
    assert len(lines) == 1
    assert "INFO" in lines[0]
    assert "hello" in lines[0]


def test_clear_removes_all_entries(logger):
    logger.info("x")
    logger.error("y")
    logger.clear()
    assert logger.entries == []


def test_log_entry_str_format():
    entry = LogEntry(level=LogLevel.WARNING, message="test msg", timestamp="2024-01-01T00:00:00")
    result = str(entry)
    assert "WARNING" in result
    assert "test msg" in result
    assert "2024-01-01T00:00:00" in result
