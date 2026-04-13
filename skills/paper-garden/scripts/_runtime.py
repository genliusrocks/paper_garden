from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
import argparse
import re
import shutil
import subprocess
import tomllib
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class ConfigurationRequiredError(ValueError):
    pass


SAFE_RE = re.compile(r"[^a-z0-9]+")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class PaperGardenConfig:
    garden_dir: Path
    language: str


@dataclass(frozen=True)
class DownloadedPaper:
    arxiv_id: str | None
    title: str
    paper_slug: str
    pdf_path: Path
    source_kind: str
    source_ref: str


def load_config(config_path: Path) -> PaperGardenConfig:
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing config file: {config_path}")
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    garden_dir = data.get("garden_dir")
    language = data.get("language")
    if not isinstance(garden_dir, str) or not garden_dir.strip():
        raise ConfigurationRequiredError(
            "Paper Garden is not configured. Run "
            "`uv run python skills/paper-garden/scripts/configure.py --garden-dir ... --language ...`."
        )
    if not isinstance(language, str) or not language.strip():
        raise ConfigurationRequiredError(
            "Paper Garden is not configured. Run "
            "`uv run python skills/paper-garden/scripts/configure.py --garden-dir ... --language ...`."
        )
    garden_dir_path = Path(garden_dir).expanduser()
    if not garden_dir_path.is_absolute():
        garden_dir_path = (Path.cwd() / garden_dir_path).resolve()
    return PaperGardenConfig(garden_dir=garden_dir_path, language=language.strip())


def ensure_garden(garden_dir: Path) -> None:
    garden_dir.mkdir(parents=True, exist_ok=True)
    (garden_dir / "papers").mkdir(exist_ok=True)
    (garden_dir / "tags").mkdir(exist_ok=True)
    index_path = garden_dir / "index.md"
    if not index_path.exists():
        index_path.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")


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


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "paper-garden/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "paper-garden/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def fetch_title(arxiv_id: str) -> str:
    html = fetch_text(f"https://arxiv.org/abs/{arxiv_id}")
    match = TITLE_RE.search(html)
    if not match:
        return arxiv_id
    text = " ".join(unescape(match.group(1)).split())
    if " arXiv" in text:
        text = text.split(" arXiv", 1)[0].strip()
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    return text or arxiv_id


def download_paper(input_value: str, papers_dir: Path) -> DownloadedPaper:
    if is_local_pdf(input_value):
        source_path = Path(input_value).expanduser().resolve()
        title = source_path.stem
        paper_slug = slugify_title(title)
        paper_dir = papers_dir / paper_slug
        paper_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = paper_dir / "paper.pdf"
        shutil.copyfile(source_path, pdf_path)
        return DownloadedPaper(
            arxiv_id=None,
            title=title,
            paper_slug=paper_slug,
            pdf_path=pdf_path,
            source_kind="local",
            source_ref=str(source_path),
        )

    arxiv_id = canonical_arxiv_id(input_value)
    title = fetch_title(arxiv_id)
    paper_slug = f"{arxiv_id.replace('/', '_')}_{slugify_title(title)}"
    paper_dir = papers_dir / paper_slug
    paper_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = paper_dir / "paper.pdf"
    pdf_path.write_bytes(fetch_bytes(build_pdf_url(arxiv_id)))
    return DownloadedPaper(
        arxiv_id=arxiv_id,
        title=title,
        paper_slug=paper_slug,
        pdf_path=pdf_path,
        source_kind="arxiv",
        source_ref=f"https://arxiv.org/abs/{arxiv_id}",
    )


def find_extracted_files(extracted_dir: Path) -> tuple[Path, Path]:
    markdown_candidates = sorted(extracted_dir.rglob("*.md"))
    json_candidates = sorted(extracted_dir.rglob("*.json"))
    if not markdown_candidates:
        raise FileNotFoundError(f"No markdown files found under {extracted_dir}")
    if not json_candidates:
        raise FileNotFoundError(f"No JSON files found under {extracted_dir}")
    preferred_markdown = [p for p in markdown_candidates if p.name.lower() in {"document.md", "output.md"}]
    preferred_json = [p for p in json_candidates if p.name.lower() in {"document.json", "output.json"}]
    return (
        preferred_markdown[0] if preferred_markdown else markdown_candidates[0],
        preferred_json[0] if preferred_json else json_candidates[0],
    )


def run_marker(pdf_path: Path, paper_dir: Path) -> tuple[Path, Path]:
    extracted_dir = paper_dir / "extracted"
    extracted_dir.mkdir(exist_ok=True)
    subprocess.run(
        [
            "uvx",
            "--from",
            "marker-pdf",
            "marker_single",
            str(pdf_path),
            "--output_dir",
            str(extracted_dir),
        ],
        check=True,
    )
    return find_extracted_files(extracted_dir)


def build_wiki(title: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## Summary",
            "- Generated from extracted paper content.",
            "",
            "## Problem",
            "- Fill with durable problem statement from the paper.",
            "",
            "## Method",
            "- Fill with the paper's core method.",
            "",
            "## Results",
            "- Fill with the main reported findings.",
            "",
            "## Limitations",
            "- Fill with explicit limitations or caveats.",
            "",
            "## Terms",
            "- Add stable terminology here.",
            "",
        ]
    )


def write_metadata(
    paper_dir: Path,
    arxiv_id: str | None,
    title: str,
    source_ref: str,
    source_kind: str,
    language: str,
    tags: list[str],
) -> None:
    lines = [f'title = "{title}"', f'source_ref = "{source_ref}"', f'source_kind = "{source_kind}"']
    if arxiv_id:
        lines.insert(0, f'arxiv_id = "{arxiv_id}"')
    lines.append(f'language = "{language}"')
    lines.append("tags = [" + ", ".join(f'"{tag}"' for tag in tags) + "]")
    (paper_dir / "metadata.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index(index_path: Path, title: str, paper_rel_dir: str, tags: list[str]) -> None:
    entry = f"- [{title}]({paper_rel_dir}/wiki.md) | tags: {', '.join(tags)}"
    lines = index_path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"- [{title}](")]
    kept.append(entry)
    index_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")


def update_tag_files(tags_dir: Path, title: str, paper_rel_dir: str, tags: list[str]) -> None:
    for tag in tags:
        tag_path = tags_dir / f"{tag}.md"
        if tag_path.exists():
            lines = tag_path.read_text(encoding="utf-8").splitlines()
        else:
            lines = [f"# {tag}", ""]
        entry = f"- [{title}]({paper_rel_dir}/wiki.md)"
        lines = [line for line in lines if line != entry]
        lines.append(entry)
        tag_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one paper into Paper Garden.")
    parser.add_argument("input_value", help="arXiv abs/html/pdf URL, arXiv id, or local PDF path.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "paper_garden.toml"),
        help="Path to paper_garden.toml.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(Path(args.config))
    ensure_garden(config.garden_dir)
    paper = download_paper(args.input_value, config.garden_dir / "papers")
    markdown_path, _json_path = run_marker(paper.pdf_path, paper.pdf_path.parent)
    (paper.pdf_path.parent / "wiki.md").write_text(build_wiki(paper.title), encoding="utf-8")
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
    print(paper.pdf_path.parent / "wiki.md")
    return 0
