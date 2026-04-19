from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class DependencyGraph:
    _deps: Dict[str, Set[str]] = field(default_factory=dict)
    _rdeps: Dict[str, Set[str]] = field(default_factory=dict)

    def add(self, asset: str, depends_on: List[str]) -> None:
        if asset not in self._deps:
            self._deps[asset] = set()
        for dep in depends_on:
            self._deps[asset].add(dep)
            if dep not in self._rdeps:
                self._rdeps[dep] = set()
            self._rdeps[dep].add(asset)

    def dependencies(self, asset: str) -> List[str]:
        return sorted(self._deps.get(asset, set()))

    def dependents(self, asset: str) -> List[str]:
        return sorted(self._rdeps.get(asset, set()))

    def all_assets(self) -> List[str]:
        keys = set(self._deps.keys()) | set(self._rdeps.keys())
        return sorted(keys)

    def remove(self, asset: str) -> None:
        for dep in self._deps.pop(asset, set()):
            self._rdeps.get(dep, set()).discard(asset)
        for src in self._rdeps.pop(asset, set()):
            self._deps.get(src, set()).discard(asset)

    def affected_by(self, changed: str) -> List[str]:
        """Return all assets that transitively depend on changed."""
        visited: Set[str] = set()
        queue = list(self._rdeps.get(changed, set()))
        while queue:
            node = queue.pop()
            if node in visited:
                continue
            visited.add(node)
            queue.extend(self._rdeps.get(node, set()))
        return sorted(visited)

    def has_cycle(self) -> bool:
        """Return True if the dependency graph contains a cycle."""
        # Kahn's algorithm: repeatedly remove nodes with no dependencies.
        in_degree: Dict[str, int] = {a: len(self._deps.get(a, set())) for a in self.all_assets()}
        queue = [a for a, d in in_degree.items() if d == 0]
        visited_count = 0
        while queue:
            node = queue.pop()
            visited_count += 1
            for dependent in self._rdeps.get(node, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        return visited_count != len(in_degree)


def build_graph_from_manifest(manifest) -> DependencyGraph:
    graph = DependencyGraph()
    for asset in manifest.all_assets():
        path = Path(asset)
        deps = [str(path.parent / p) for p in _infer_deps(path)]
        if deps:
            graph.add(asset, deps)
        else:
            graph.add(asset, [])
    return graph


def _infer_deps(path: Path) -> List[str]:
    """Heuristic: CSS/JS files may reference others by naming convention."""
    stem = path.stem
    if stem.endswith(".min"):
        base = stem[:-4]
        return [path.with_name(base + path.suffix).name]
    return []
