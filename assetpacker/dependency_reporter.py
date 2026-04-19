from __future__ import annotations
from typing import List
from assetpacker.dependency_graph import DependencyGraph


def report_text(graph: DependencyGraph) -> str:
    lines: List[str] = ["Dependency Report", "=" * 40]
    for asset in graph.all_assets():
        deps = graph.dependencies(asset)
        rdeps = graph.dependents(asset)
        lines.append(f"\n{asset}")
        if deps:
            lines.append(f"  depends on: {', '.join(deps)}")
        if rdeps:
            lines.append(f"  required by: {', '.join(rdeps)}")
        if not deps and not rdeps:
            lines.append("  (isolated)")
    return "\n".join(lines)


def report_dot(graph: DependencyGraph) -> str:
    lines = ["digraph assets {"]
    for asset in graph.all_assets():
        safe = _dot_id(asset)
        lines.append(f'  "{safe}";')
    for asset in graph.all_assets():
        for dep in graph.dependencies(asset):
            lines.append(f'  "{_dot_id(asset)}" -> "{_dot_id(dep)}";')
    lines.append("}")
    return "\n".join(lines)


def impact_summary(graph: DependencyGraph, changed: List[str]) -> str:
    all_affected: set = set()
    for c in changed:
        all_affected.update(graph.affected_by(c))
    lines = [f"Changed: {len(changed)} file(s)"]
    lines.append(f"Affected by change: {len(all_affected)} asset(s)")
    for a in sorted(all_affected):
        lines.append(f"  - {a}")
    return "\n".join(lines)


def _dot_id(name: str) -> str:
    return name.replace("\\", "/")
