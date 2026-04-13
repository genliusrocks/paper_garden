from __future__ import annotations

from pathlib import Path


def build_wiki(title: str, extracted_markdown: str, language: str) -> str:
    _ = extracted_markdown
    _ = language
    return "\n".join(
        [
            f"# {title}",
            "",
            "## Summary",
            "- Generated from extracted paper content.",
            "",
            "## Problem",
            "- Fill with durable problem statement from the paper.",
            "",
            "## Method",
            "- Fill with the paper's core method.",
            "",
            "## Results",
            "- Fill with the main reported findings.",
            "",
            "## Limitations",
            "- Fill with explicit limitations or caveats.",
            "",
            "## Terms",
            "- Add stable terminology here.",
            "",
        ]
    )


def write_wiki(paper_dir: Path, title: str, extracted_markdown: str, language: str) -> Path:
    wiki_path = paper_dir / "wiki.md"
    wiki_path.write_text(build_wiki(title, extracted_markdown, language), encoding="utf-8")
    return wiki_path
