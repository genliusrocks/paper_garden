#!/usr/bin/env python3
"""Download a paper and extract content with marker. Outputs JSON with paths."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

from paper_garden.config import load_config
from paper_garden.dedup import check_duplicate
from paper_garden.download import download_paper, resolve_paper
from paper_garden.extract import run_marker
from paper_garden.init import ensure_garden

import requests


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and extract a paper.")
    parser.add_argument("input_value", help="arXiv URL/ID or local PDF path.")
    parser.add_argument("--config", required=True, help="Path to paper_garden.toml.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    ensure_garden(config.garden_dir, language=config.language)

    with requests.Session() as session:
        # Resolve title before downloading to check for duplicates first
        resolved = resolve_paper(session, args.input_value)

        dup = check_duplicate(config.garden_dir / "index.md", resolved.title)
        if dup.found:
            result = {
                "duplicate": True,
                "title": resolved.title,
                "existing_entry": dup.existing_entry,
                "existing_paper_dir": str(config.garden_dir / dup.existing_paper_dir) if dup.existing_paper_dir else None,
                "garden_dir": str(config.garden_dir),
            }
            print(json.dumps(result, indent=2))
            return 0

        paper = download_paper(session, args.input_value, config.garden_dir / "papers")

    extraction = run_marker(paper.pdf_path, paper.pdf_path.parent)

    result = {
        "duplicate": False,
        "paper_dir": str(paper.pdf_path.parent),
        "paper_slug": paper.paper_slug,
        "title": paper.title,
        "arxiv_id": paper.arxiv_id,
        "source_kind": paper.source_kind,
        "source_ref": paper.source_ref,
        "extracted_markdown": str(extraction.markdown_path),
        "extracted_json": str(extraction.json_path),
        "garden_dir": str(config.garden_dir),
        "language": config.language,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
