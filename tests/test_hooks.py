"""Tests for assetpacker.hooks."""
import pytest

from assetpacker.hooks import (
    HookConfig,
    HookResult,
    collect_warnings,
    run_hook,
    run_hooks,
)


def test_hook_result_success():
    r = HookResult(command="echo hi", returncode=0, stdout="hi", stderr="")
    assert r.success is True


def test_hook_result_failure():
    r = HookResult(command="false", returncode=1, stdout="", stderr="err")
    assert r.success is False


def test_run_hook_success():
    result = run_hook("echo hello")
    assert result.success
    assert "hello" in result.stdout


def test_run_hook_failure():
    result = run_hook("exit 1")
    assert not result.success
    assert result.returncode == 1


def test_run_hooks_all_succeed():
    results = run_hooks(["echo a", "echo b"])
    assert len(results) == 2
    assert all(r.success for r in results)


def test_run_hooks_stops_on_failure():
    results = run_hooks(["echo a", "exit 2", "echo c"])
    assert len(results) == 2
    assert not results[-1].success


def test_run_hooks_empty():
    assert run_hooks([]) == []


def test_collect_warnings_none():
    results = [HookResult("echo", 0, "ok", "")]
    assert collect_warnings(results) == []


def test_collect_warnings_with_failure():
    results = [
        HookResult("echo ok", 0, "ok", ""),
        HookResult("bad_cmd", 127, "", "not found"),
    ]
    warnings = collect_warnings(results)
    assert len(warnings) == 1
    assert "bad_cmd" in warnings[0]
    assert "rc=127" in warnings[0]


def test_hook_config_from_dict():
    cfg = HookConfig.from_dict({"pre_build": ["echo pre"], "post_build": ["echo post"]})
    assert cfg.pre_build == ["echo pre"]
    assert cfg.post_build == ["echo post"]


def test_hook_config_defaults():
    cfg = HookConfig.from_dict({})
    assert cfg.pre_build == []
    assert cfg.post_build == []
