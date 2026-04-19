"""Resolve tags from config patterns and apply them to an asset manifest."""

import fnmatch
from typing import Dict, List
from assetpacker.scanner import AssetManifest
from assetpacker.tag_index import TagIndex, build_tag_index


TagRules = List[Dict]  # each: {"pattern": "*.png", "tags": ["image", "sprite"]}


def resolve_tags(manifest: AssetManifest, rules: TagRules) -> Dict[str, List[str]]:
    """Match asset paths against glob rules and collect tags per path."""
    all_paths = manifest.all_assets()
    tag_map: Dict[str, List[str]] = {}
    for path in all_paths:
        matched: List[str] = []
        for rule in rules:
            pattern = rule.get("pattern", "")
            tags = rule.get("tags", [])
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path.split("/")[-1], pattern):
                matched.extend(tags)
        if matched:
            tag_map[path] = matched
    return tag_map


def build_index_from_rules(manifest: AssetManifest, rules: TagRules) -> TagIndex:
    """Convenience: resolve tags from rules and return a built TagIndex."""
    tag_map = resolve_tags(manifest, rules)
    return build_tag_index(manifest, tag_map)


def describe_rules(rules: TagRules) -> List[str]:
    """Return human-readable descriptions of each tag rule."""
    lines = []
    for rule in rules:
        pattern = rule.get("pattern", "(none)")
        tags = ", ".join(rule.get("tags", []))
        lines.append(f"  {pattern!r} -> [{tags}]")
    return lines
