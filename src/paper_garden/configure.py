from __future__ import annotations

from pathlib import Path
import argparse

import tomli_w


DEFAULT_GARDEN_DIR = "./paper_garden"
DEFAULT_LANGUAGE = "en"


def write_config(config_path: Path, garden_dir: str | None, language: str | None) -> Path:
    resolved_garden_dir = garden_dir or DEFAULT_GARDEN_DIR
    resolved_language = language or DEFAULT_LANGUAGE
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        tomli_w.dumps(
            {
                "garden_dir": resolved_garden_dir,
                "language": resolved_language,
            }
        ),
        encoding="utf-8",
    )
    return config_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Paper Garden skill settings.")
    parser.add_argument("--garden-dir", default=None, help="Output directory for the paper garden.")
    parser.add_argument("--language", default=None, help="Content generation language.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "skills" / "paper-garden" / "paper_garden.toml"),
        help="Path to paper_garden.toml.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = write_config(Path(args.config), args.garden_dir, args.language)
    print(config_path)
    return 0
