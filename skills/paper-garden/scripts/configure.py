#!/usr/bin/env python3
"""Configure Paper Garden settings."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

from paper_garden.configure import write_config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Paper Garden skill settings.")
    parser.add_argument("--garden-dir", default=None, help="Output directory for the paper garden.")
    parser.add_argument("--language", default=None, help="Content generation language.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "paper_garden.toml"),
        help="Path to paper_garden.toml.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = write_config(Path(args.config), args.garden_dir, args.language)
    print(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
