from __future__ import annotations

from pathlib import Path
import argparse

import requests
import tomli_w

from paper_garden.config import load_config
from paper_garden.download import download_paper
from paper_garden.extract import run_marker
from paper_garden.index import update_index
from paper_garden.init import ensure_garden
from paper_garden.tags import update_tag_files
from paper_garden.wiki import write_wiki


def write_metadata(
    paper_dir: Path,
    arxiv_id: str | None,
    title: str,
    source_ref: str,
    source_kind: str,
    language: str,
    tags: list[str],
) -> Path:
    data = {
        "title": title,
        "source_ref": source_ref,
        "source_kind": source_kind,
        "language": language,
        "tags": tags,
    }
    if arxiv_id:
        data["arxiv_id"] = arxiv_id

    metadata_path = paper_dir / "metadata.toml"
    metadata_path.write_text(
        tomli_w.dumps(data),
        encoding="utf-8",
    )
    return metadata_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one arXiv paper into Paper Garden.")
    parser.add_argument("input_value", help="arXiv abs/html/pdf URL or arXiv id.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "skills" / "paper-garden" / "paper_garden.toml"),
        help="Path to paper_garden.toml.",
    )
    parser.add_argument(
        "--tags",
        default=None,
        help="Comma-separated tags. If omitted, defaults to source-based tag.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    ensure_garden(config.garden_dir)

    with requests.Session() as session:
        paper = download_paper(session, args.input_value, config.garden_dir / "papers")
        extraction = run_marker(paper.pdf_path, paper.pdf_path.parent)

    wiki_path = paper.pdf_path.parent / "wiki.md"
    if not wiki_path.exists():
        write_wiki(
            paper.pdf_path.parent,
            paper.title,
            extraction.markdown_path.read_text(encoding="utf-8"),
            config.language,
        )

    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    else:
        tags = ["arxiv"] if paper.source_kind == "arxiv" else ["local-pdf"]

    write_metadata(
        paper.pdf_path.parent,
        paper.arxiv_id,
        paper.title,
        paper.source_ref,
        paper.source_kind,
        config.language,
        tags,
    )
    paper_rel_dir = f"papers/{paper.paper_slug}"
    update_index(config.garden_dir / "index.md", paper.title, paper_rel_dir, tags)
    update_tag_files(config.garden_dir / "tags", paper.title, paper_rel_dir, tags)

    print(paper.pdf_path.parent)
    return 0
