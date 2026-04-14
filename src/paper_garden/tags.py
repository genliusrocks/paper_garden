from __future__ import annotations

from pathlib import Path


def _extract_existing_summary(lines: list[str], title: str) -> str | None:
    for line in lines:
        if f"[{title}](" in line and " — " in line:
            return line.rsplit(" — ", 1)[1]
    return None


def update_tag_files(tags_dir: Path, title: str, paper_rel_dir: str, tags: list[str], year: str | None = None, summary: str | None = None) -> None:
    year_prefix = f"({year}) " if year else ""
    for tag in tags:
        tag_path = tags_dir / f"{tag}.md"
        if tag_path.exists():
            lines = tag_path.read_text(encoding="utf-8").splitlines()
        else:
            lines = [f"# {tag}", ""]
        if summary is None:
            summary = _extract_existing_summary(lines, title)
        summary_suffix = f" — {summary}" if summary else ""
        entry = f"- {year_prefix}[{title}]({paper_rel_dir}/wiki.md){summary_suffix}"
        lines = [line for line in lines if f"[{title}]({paper_rel_dir}/wiki.md)" not in line]
        lines.append(entry)
        tag_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
