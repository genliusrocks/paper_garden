from __future__ import annotations

from pathlib import Path

from paper_garden.dedup import normalize_title


def _extract_existing_summary(lines: list[str], normalized: str) -> str | None:
    for line in lines:
        bracket_start = line.find("[")
        bracket_end = line.find("](")
        if bracket_start < 0 or bracket_end < 0:
            continue
        existing = line[bracket_start + 1 : bracket_end]
        if normalize_title(existing) == normalized and " — " in line:
            return line.rsplit(" — ", 1)[1]
    return None


def update_index(index_path: Path, title: str, paper_rel_dir: str, tags: list[str], year: str | None = None, summary: str | None = None) -> None:
    normalized = normalize_title(title)
    year_prefix = f"({year}) " if year else ""
    lines = index_path.read_text(encoding="utf-8").splitlines()
    if summary is None:
        summary = _extract_existing_summary(lines, normalized)
    summary_suffix = f" — {summary}" if summary else ""
    entry = f"- {year_prefix}[{title}]({paper_rel_dir}/wiki.md) | tags: {', '.join(tags)}{summary_suffix}"
    # Remove any existing entry for this paper (by normalized title match)
    kept = []
    for line in lines:
        bracket_start = line.find("[")
        bracket_end = line.find("](")
        if bracket_start >= 0 and bracket_end >= 0:
            existing = line[bracket_start + 1 : bracket_end]
            if normalize_title(existing) == normalized:
                continue
        kept.append(line)
    kept.append(entry)
    index_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
