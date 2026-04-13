from __future__ import annotations

from pathlib import Path


DEFAULT_INDEX = "# Paper Garden\n\n## Papers\n\n"


def ensure_garden(garden_dir: Path) -> None:
    garden_dir.mkdir(parents=True, exist_ok=True)
    (garden_dir / "papers").mkdir(exist_ok=True)
    (garden_dir / "tags").mkdir(exist_ok=True)

    index_path = garden_dir / "index.md"
    if not index_path.exists():
        index_path.write_text(DEFAULT_INDEX, encoding="utf-8")
