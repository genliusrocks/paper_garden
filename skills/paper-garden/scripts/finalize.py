#!/usr/bin/env python3
"""Write metadata and update garden index/tag files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

from paper_garden.config import load_config
from paper_garden.ingest import write_metadata
from paper_garden.index import update_index
from paper_garden.tags import update_tag_files


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize paper ingest: metadata, index, tags.")
    parser.add_argument("--config", required=True, help="Path to paper_garden.toml.")
    parser.add_argument("--paper-dir", required=True, help="Path to the paper directory.")
    parser.add_argument("--title", required=True, help="Paper title.")
    parser.add_argument("--paper-slug", required=True, help="Filesystem-safe paper slug.")
    parser.add_argument("--tags", required=True, help="Comma-separated tags.")
    parser.add_argument("--arxiv-id", default=None, help="arXiv paper ID.")
    parser.add_argument("--source-ref", required=True, help="Source URL or path.")
    parser.add_argument("--source-kind", required=True, help="Source type: arxiv or local.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    paper_dir = Path(args.paper_dir)

    write_metadata(
        paper_dir=paper_dir,
        arxiv_id=args.arxiv_id,
        title=args.title,
        source_ref=args.source_ref,
        source_kind=args.source_kind,
        language=config.language,
        tags=tags,
    )

    paper_rel_dir = f"papers/{args.paper_slug}"
    update_index(config.garden_dir / "index.md", args.title, paper_rel_dir, tags)
    update_tag_files(config.garden_dir / "tags", args.title, paper_rel_dir, tags)

    print(f"Updated metadata, index, and {len(tags)} tag file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
