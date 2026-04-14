from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


SAFE_RE = re.compile(r"[^a-z0-9]+")
ARXIV_YYMM_RE = re.compile(r"^(\d{2})(\d{2})\.")


def year_from_arxiv_id(arxiv_id: str | None) -> str | None:
    if not arxiv_id:
        return None
    m = ARXIV_YYMM_RE.match(arxiv_id)
    if not m:
        return None
    yy = int(m.group(1))
    return str(2000 + yy) if yy < 100 else None


@dataclass(frozen=True)
class DownloadedPaper:
    arxiv_id: str | None
    title: str
    paper_slug: str
    pdf_path: Path
    source_kind: str
    source_ref: str


def canonical_arxiv_id(value: str) -> str:
    candidate = value.strip()
    parsed = urlparse(candidate)
    if parsed.scheme and parsed.netloc:
        if parsed.netloc != "arxiv.org":
            raise ValueError("Input must point to arxiv.org")
        path = parsed.path.rstrip("/")
        if path.startswith("/abs/"):
            return path.split("/abs/", 1)[1]
        if path.startswith("/html/"):
            return path.split("/html/", 1)[1]
        if path.startswith("/pdf/"):
            tail = path.split("/pdf/", 1)[1]
            return tail[:-4] if tail.endswith(".pdf") else tail
        raise ValueError("Unsupported arXiv URL")
    if not candidate:
        raise ValueError("Input cannot be empty")
    return candidate


def build_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{canonical_arxiv_id(arxiv_id)}.pdf"


def slugify_title(title: str) -> str:
    slug = SAFE_RE.sub("_", title.lower()).strip("_")
    return slug or "paper"


def is_local_pdf(input_value: str) -> bool:
    path = Path(input_value).expanduser()
    return path.is_file() and path.suffix.lower() == ".pdf"


def fetch_title(session: requests.Session, arxiv_id: str) -> str:
    abs_url = f"https://arxiv.org/abs/{arxiv_id}"
    response = session.get(abs_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.select_one("h1.title")
    text = node.get_text(" ", strip=True) if node else arxiv_id
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    return text or arxiv_id


@dataclass(frozen=True)
class ResolvedPaper:
    """Metadata resolved before downloading the PDF."""
    arxiv_id: str | None
    title: str
    paper_slug: str
    source_kind: str
    source_ref: str
    year: str | None


def resolve_paper(session: requests.Session | None, input_value: str) -> ResolvedPaper:
    """Resolve paper metadata (title, slug, source, year) without downloading the PDF."""
    if is_local_pdf(input_value):
        source_path = Path(input_value).expanduser().resolve()
        title = source_path.stem
        return ResolvedPaper(
            arxiv_id=None,
            title=title,
            paper_slug=slugify_title(title),
            source_kind="local",
            source_ref=str(source_path),
            year=None,
        )

    arxiv_id = canonical_arxiv_id(input_value)
    if session is None:
        raise ValueError("requests.Session required for arXiv downloads")
    title = fetch_title(session, arxiv_id)
    return ResolvedPaper(
        arxiv_id=arxiv_id,
        title=title,
        paper_slug=f"{arxiv_id.replace('/', '_')}_{slugify_title(title)}",
        source_kind="arxiv",
        source_ref=f"https://arxiv.org/abs/{arxiv_id}",
        year=year_from_arxiv_id(arxiv_id),
    )


def download_paper(session: requests.Session, input_value: str, papers_dir: Path) -> DownloadedPaper:
    resolved = resolve_paper(session, input_value)
    paper_dir = papers_dir / resolved.paper_slug
    paper_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = paper_dir / "paper.pdf"

    if resolved.source_kind == "local":
        source_path = Path(resolved.source_ref)
        shutil.copyfile(source_path, pdf_path)
    else:
        response = session.get(build_pdf_url(resolved.arxiv_id), timeout=30)
        response.raise_for_status()
        pdf_path.write_bytes(response.content)

    return DownloadedPaper(
        arxiv_id=resolved.arxiv_id,
        title=resolved.title,
        paper_slug=resolved.paper_slug,
        pdf_path=pdf_path,
        source_kind=resolved.source_kind,
        source_ref=resolved.source_ref,
    )
