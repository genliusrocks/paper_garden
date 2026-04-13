from __future__ import annotations

from pathlib import Path


def update_tag_files(tags_dir: Path, title: str, paper_rel_dir: str, tags: list[str]) -> None:
    for tag in tags:
        tag_path = tags_dir / f"{tag}.md"
        if tag_path.exists():
            lines = tag_path.read_text(encoding="utf-8").splitlines()
        else:
            lines = [f"# {tag}", ""]
        entry = f"- [{title}]({paper_rel_dir}/wiki.md)"
        lines = [line for line in lines if line != entry]
        lines.append(entry)
        tag_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
