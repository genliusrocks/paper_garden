from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


SAFE_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class DownloadedPaper:
    arxiv_id: str
    title: str
    paper_slug: str
    pdf_path: Path
    abs_url: str


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


def download_paper(session: requests.Session, input_value: str, papers_dir: Path) -> DownloadedPaper:
    arxiv_id = canonical_arxiv_id(input_value)
    title = fetch_title(session, arxiv_id)
    paper_slug = f"{arxiv_id.replace('/', '_')}_{slugify_title(title)}"
    paper_dir = papers_dir / paper_slug
    paper_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = paper_dir / "paper.pdf"
    response = session.get(build_pdf_url(arxiv_id), timeout=30)
    response.raise_for_status()
    pdf_path.write_bytes(response.content)
    return DownloadedPaper(
        arxiv_id=arxiv_id,
        title=title,
        paper_slug=paper_slug,
        pdf_path=pdf_path,
        abs_url=f"https://arxiv.org/abs/{arxiv_id}",
    )
