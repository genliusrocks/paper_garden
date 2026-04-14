from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_title(title: str) -> str:
    """Normalize a title for dedup matching only.

    Applies: lowercase, underscores to spaces, collapse whitespace.
    Preserves punctuation so PointNet != PointNet++.
    """
    lowered = title.lower().strip().replace("_", " ")
    return MULTI_SPACE_RE.sub(" ", lowered).strip()


@dataclass(frozen=True)
class DuplicateResult:
    found: bool
    existing_entry: str | None = None
    existing_paper_dir: str | None = None


def check_duplicate(index_path: Path, title: str) -> DuplicateResult:
    """Check if a paper with the same normalized title exists in index.md."""
    if not index_path.is_file():
        return DuplicateResult(found=False)

    normalized = normalize_title(title)
    lines = index_path.read_text(encoding="utf-8").splitlines()

    for line in lines:
        if not line.startswith("- "):
            continue
        # Extract title from markdown link: [Title](path/wiki.md)
        bracket_start = line.find("[")
        bracket_end = line.find("](")
        if bracket_start < 0 or bracket_end < 0:
            continue
        existing_title = line[bracket_start + 1 : bracket_end]
        if normalize_title(existing_title) == normalized:
            # Extract paper dir from link
            paren_end = line.find(")", bracket_end)
            link = line[bracket_end + 2 : paren_end] if paren_end > 0 else ""
            paper_dir = link.rsplit("/wiki.md", 1)[0] if "/wiki.md" in link else ""
            return DuplicateResult(
                found=True,
                existing_entry=line,
                existing_paper_dir=paper_dir,
            )

    return DuplicateResult(found=False)
