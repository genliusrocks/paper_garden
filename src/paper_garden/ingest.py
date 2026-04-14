from __future__ import annotations

from pathlib import Path
import argparse

import requests
import tomli_w

from paper_garden.config import load_config
from paper_garden.download import download_paper, year_from_arxiv_id
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
    paper_id: str,
    year: str,
) -> Path:
    data = {
        "id": paper_id,
        "year": year,
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
    parser.add_argument(
        "--year",
        default=None,
        help="Publication year (required if not derivable from arXiv ID).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    ensure_garden(config.garden_dir, language=config.language)

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

    year = args.year or year_from_arxiv_id(paper.arxiv_id)
    if not year:
        raise SystemExit("Publication year could not be inferred. Pass --year YYYY.")

    from paper_garden.ids import next_id

    index_path = config.garden_dir / "index.md"
    paper_id = next_id(index_path, year)

    write_metadata(
        paper_dir=paper.pdf_path.parent,
        arxiv_id=paper.arxiv_id,
        title=paper.title,
        source_ref=paper.source_ref,
        source_kind=paper.source_kind,
        language=config.language,
        tags=tags,
        paper_id=paper_id,
        year=year,
    )
    paper_rel_dir = f"papers/{paper.paper_slug}"
    update_index(index_path, paper_id=paper_id, title=paper.title, paper_rel_dir=paper_rel_dir, tags=tags)
    update_tag_files(config.garden_dir / "tags", paper_id=paper_id, title=paper.title, paper_rel_dir=paper_rel_dir, tags=tags)

    print(paper.pdf_path.parent)
    return 0
