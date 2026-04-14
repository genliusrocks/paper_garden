from __future__ import annotations

from pathlib import Path


def _extract_existing_summary(lines: list[str], title: str) -> str | None:
    for line in lines:
        if f"[{title}](" in line and " — " in line:
            return line.rsplit(" — ", 1)[1]
    return None


def update_index(index_path: Path, title: str, paper_rel_dir: str, tags: list[str], year: str | None = None, summary: str | None = None) -> None:
    year_prefix = f"({year}) " if year else ""
    lines = index_path.read_text(encoding="utf-8").splitlines()
    if summary is None:
        summary = _extract_existing_summary(lines, title)
    summary_suffix = f" — {summary}" if summary else ""
    entry = f"- {year_prefix}[{title}]({paper_rel_dir}/wiki.md) | tags: {', '.join(tags)}{summary_suffix}"
    kept = [line for line in lines if not line.startswith(f"- {year_prefix}[{title}](") and not line.startswith(f"- [{title}](")]
    kept.append(entry)
    index_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
