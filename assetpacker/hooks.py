"""Pre/post build hook support for assetpacker."""
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HookResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


@dataclass
class HookConfig:
    pre_build: List[str] = field(default_factory=list)
    post_build: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict) -> "HookConfig":
        return HookConfig(
            pre_build=data.get("pre_build", []),
            post_build=data.get("post_build", []),
        )


def run_hook(command: str, cwd: Optional[str] = None) -> HookResult:
    """Run a single shell hook command."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        return HookResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
        )
    except Exception as exc:  # pragma: no cover
        return HookResult(command=command, returncode=1, stdout="", stderr=str(exc))


def run_hooks(commands: List[str], cwd: Optional[str] = None) -> List[HookResult]:
    """Run a list of hook commands sequentially; stop on first failure."""
    results: List[HookResult] = []
    for cmd in commands:
        result = run_hook(cmd, cwd=cwd)
        results.append(result)
        if not result.success:
            break
    return results


def collect_warnings(results: List[HookResult]) -> List[str]:
    """Return warning strings for any failed hooks."""
    warnings = []
    for r in results:
        if not r.success:
            warnings.append(f"Hook failed (rc={r.returncode}): {r.command}")
    return warnings
