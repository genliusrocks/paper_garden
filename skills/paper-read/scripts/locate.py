#!/usr/bin/env python3
"""Locate a paper in the garden by its pg-YYYY-xxxxx ID and emit JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

from paper_garden.config import load_config
from paper_garden.locate import locate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Locate a paper by ID.")
    parser.add_argument("paper_id", help="Paper ID, e.g. pg-2024-00005")
    parser.add_argument("--config", required=True, help="Path to paper_garden.toml.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    result = locate(config.garden_dir, args.paper_id)
    if result is None:
        print(f"paper id '{args.paper_id}' not found", file=sys.stderr)
        return 1
    payload = {
        "paper_id": result.paper_id,
        "paper_dir": str(result.paper_dir),
        "wiki_path": str(result.wiki_path),
        "extracted_markdown": str(result.extracted_markdown),
        "title": result.title,
        "tags": result.tags,
        "year": result.year,
        "garden_dir": str(config.garden_dir),
        "language": config.language,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
