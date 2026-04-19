from assetpacker.stats import BuildStats


def render_text(stats: BuildStats) -> str:
    lines = []
    lines.append("=== Build Stats ===")
    lines.append(f"  Total files    : {stats.total_files}")
    lines.append(f"  Original size  : {stats.total_original_bytes:,} bytes")
    lines.append(f"  Optimized size : {stats.total_optimized_bytes:,} bytes")
    lines.append(f"  Savings        : {stats.total_savings_bytes:,} bytes ({stats.total_savings_pct}%)")
    lines.append(f"  Bundle size    : {stats.bundle_size_kb:.2f} KB")
    if stats.category_stats:
        lines.append("")
        lines.append("  By category:")
        for cat in stats.category_stats:
            lines.append(
                f"    {cat.category:<10} {cat.file_count} files, "
                f"{cat.original_bytes:,} -> {cat.optimized_bytes:,} bytes "
                f"({cat.savings_pct}% saved)"
            )
    return "\n".join(lines)


def render_compact(stats: BuildStats) -> str:
    return (
        f"{stats.total_files} files | "
        f"{stats.total_original_bytes:,}B -> {stats.total_optimized_bytes:,}B "
        f"({stats.total_savings_pct}% saved) | "
        f"bundle {stats.bundle_size_kb:.2f} KB"
    )


def render_markdown(stats: BuildStats) -> str:
    lines = []
    lines.append("## Build Stats")
    lines.append("")
    lines.append(f"- **Total files**: {stats.total_files}")
    lines.append(f"- **Original size**: {stats.total_original_bytes:,} bytes")
    lines.append(f"- **Optimized size**: {stats.total_optimized_bytes:,} bytes")
    lines.append(f"- **Savings**: {stats.total_savings_bytes:,} bytes ({stats.total_savings_pct}%)")
    lines.append(f"- **Bundle size**: {stats.bundle_size_kb:.2f} KB")
    if stats.category_stats:
        lines.append("")
        lines.append("| Category | Files | Original | Optimized | Saved |")
        lines.append("|----------|-------|----------|-----------|-------|")
        for cat in stats.category_stats:
            lines.append(
                f"| {cat.category} | {cat.file_count} | {cat.original_bytes:,} | "
                f"{cat.optimized_bytes:,} | {cat.savings_pct}% |"
            )
    return "\n".join(lines)
