from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from paper_garden.ids import ID_RE


@dataclass(frozen=True)
class LocatedPaper:
    paper_id: str
    paper_dir: Path
    wiki_path: Path
    extracted_markdown: Path
    title: str
    tags: list[str]
    year: str


def _load_metadata(paper_dir: Path) -> dict | None:
    meta_path = paper_dir / "metadata.toml"
    if not meta_path.is_file():
        return None
    return tomllib.loads(meta_path.read_text(encoding="utf-8"))


def _build_located(paper_id: str, paper_dir: Path, meta: dict) -> LocatedPaper:
    return LocatedPaper(
        paper_id=paper_id,
        paper_dir=paper_dir,
        wiki_path=paper_dir / "wiki.md",
        extracted_markdown=paper_dir / "extracted" / "document.md",
        title=str(meta.get("title", "")),
        tags=list(meta.get("tags", [])),
        year=str(meta.get("year", "")),
    )


def _locate_via_index(garden_dir: Path, paper_id: str) -> LocatedPaper | None:
    index_path = garden_dir / "index.md"
    if not index_path.is_file():
        return None
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = ID_RE.match(line)
        if not m:
            continue
        if f"pg-{m.group(1)}-{m.group(2)}" != paper_id:
            continue
        link_start = line.find("](")
        if link_start < 0:
            continue
        link_end = line.find(")", link_start + 2)
        if link_end < 0:
            continue
        wiki_rel = line[link_start + 2 : link_end]
        paper_dir = (garden_dir / wiki_rel).parent
        meta = _load_metadata(paper_dir)
        if meta is None:
            return None
        return _build_located(paper_id, paper_dir, meta)
    return None


def _locate_via_metadata(garden_dir: Path, paper_id: str) -> LocatedPaper | None:
    papers_dir = garden_dir / "papers"
    if not papers_dir.is_dir():
        return None
    for meta_path in papers_dir.glob("*/metadata.toml"):
        try:
            meta = tomllib.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if meta.get("id") == paper_id:
            return _build_located(paper_id, meta_path.parent, meta)
    return None


def locate(garden_dir: Path, paper_id: str) -> LocatedPaper | None:
    result = _locate_via_index(garden_dir, paper_id)
    if result is not None:
        return result
    return _locate_via_metadata(garden_dir, paper_id)
