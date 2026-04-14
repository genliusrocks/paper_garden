from __future__ import annotations

from pathlib import Path

from paper_garden.ids import ID_RE


def _extract_existing_summary(lines: list[str], paper_id: str) -> str | None:
    for line in lines:
        m = ID_RE.match(line)
        if m and f"pg-{m.group(1)}-{m.group(2)}" == paper_id and " — " in line:
            return line.rsplit(" — ", 1)[1]
    return None


def update_tag_files(
    tags_dir: Path,
    paper_id: str,
    title: str,
    paper_rel_dir: str,
    tags: list[str],
    summary: str | None = None,
) -> None:
    for tag in tags:
        tag_path = tags_dir / f"{tag}.md"
        if tag_path.exists():
            lines = tag_path.read_text(encoding="utf-8").splitlines()
        else:
            lines = [f"# {tag}", ""]
        effective_summary = summary if summary is not None else _extract_existing_summary(lines, paper_id)
        summary_suffix = f" — {effective_summary}" if effective_summary else ""
        entry = f"- `{paper_id}` [{title}]({paper_rel_dir}/wiki.md){summary_suffix}"
        kept: list[str] = []
        for line in lines:
            m = ID_RE.match(line)
            if m and f"pg-{m.group(1)}-{m.group(2)}" == paper_id:
                continue
            kept.append(line)
        kept.append(entry)
        tag_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
