from __future__ import annotations

from pathlib import Path


def update_index(index_path: Path, title: str, paper_rel_dir: str, tags: list[str]) -> None:
    entry = f"- [{title}]({paper_rel_dir}/wiki.md) | tags: {', '.join(tags)}"
    lines = index_path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"- [{title}](")]
    kept.append(entry)
    index_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
