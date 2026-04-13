# Paper Garden Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public Codex skill that ingests one arXiv paper into a Markdown-based paper garden with PDF download, marker extraction, wiki generation, and index/tag updates.

**Architecture:** Keep the public entrypoint in `skills/paper-garden/`, but implement the workflow as small Python modules under `src/paper_garden/`. The skill wrapper reads skill-local config, then calls one orchestrator that initializes the garden, downloads the paper, extracts Markdown, generates a wiki, and updates deterministic index files.

**Tech Stack:** Python 3.12+, `uv`, `pytest`, `requests`, `beautifulsoup4`, `tomli-w`, `marker-pdf`

---

## File Map

Create these files:

- `pyproject.toml`
- `README.md`
- `skills/paper-garden/SKILL.md`
- `skills/paper-garden/paper_garden.toml`
- `skills/paper-garden/scripts/run.py`
- `src/paper_garden/__init__.py`
- `src/paper_garden/config.py`
- `src/paper_garden/init.py`
- `src/paper_garden/download.py`
- `src/paper_garden/extract.py`
- `src/paper_garden/wiki.py`
- `src/paper_garden/tags.py`
- `src/paper_garden/index.py`
- `src/paper_garden/ingest.py`
- `templates/index.md`
- `templates/tag.md`
- `templates/wiki.md`
- `tests/test_config.py`
- `tests/test_init.py`
- `tests/test_download.py`
- `tests/test_index.py`
- `tests/test_tags.py`
- `tests/test_ingest.py`

Modify these files later in the plan:

- `README.md`
- `skills/paper-garden/SKILL.md`
- `skills/paper-garden/scripts/run.py`
- `src/paper_garden/*.py`

### Task 1: Scaffold Repository Metadata And Skill Entry

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `skills/paper-garden/SKILL.md`
- Create: `skills/paper-garden/paper_garden.toml`
- Create: `skills/paper-garden/scripts/run.py`
- Create: `src/paper_garden/__init__.py`

- [ ] **Step 1: Create project metadata**

```toml
[project]
name = "paper-garden"
version = "0.1.0"
description = "Codex skill for ingesting arXiv papers into a Markdown garden"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
  "beautifulsoup4>=4.12",
  "requests>=2.32",
  "tomli-w>=1.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Add a minimal package marker**

```python
__all__ = [
    "config",
    "download",
    "extract",
    "index",
    "ingest",
    "init",
    "tags",
    "wiki",
]
```

- [ ] **Step 3: Add initial skill config**

```toml
garden_dir = "./paper_garden"
language = "en"
```

- [ ] **Step 4: Add the initial skill wrapper**

```python
#!/usr/bin/env python3

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paper_garden.ingest import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add the initial skill definition**

```md
---
name: paper-garden
description: Ingest one arXiv paper into the configured Markdown paper garden.
---

# Paper Garden

Use this skill when the user wants to ingest a single arXiv paper into the configured garden.

## Workflow

1. Read `paper_garden.toml` from this skill directory.
2. Run:

```bash
uv run python skills/paper-garden/scripts/run.py "<arxiv_url_or_id>"
```

3. Report the created paper directory, wiki path, and updated index files.
```

- [ ] **Step 6: Add the initial README skeleton**

```md
# Paper Garden

Paper Garden is a Codex skill for ingesting a single arXiv paper into a Markdown-based knowledge garden.

## Status

Initial public release in progress.
```

- [ ] **Step 7: Commit the scaffolding**

```bash
git add pyproject.toml README.md skills/paper-garden/SKILL.md skills/paper-garden/paper_garden.toml skills/paper-garden/scripts/run.py src/paper_garden/__init__.py
git commit -m "chore: scaffold paper garden skill package"
```

### Task 2: Implement Config Loading And Garden Initialization

**Files:**
- Create: `src/paper_garden/config.py`
- Create: `src/paper_garden/init.py`
- Create: `tests/test_config.py`
- Create: `tests/test_init.py`

- [ ] **Step 1: Write the failing config tests**

```python
from pathlib import Path

from paper_garden.config import load_config


def test_load_config_reads_skill_local_file(tmp_path: Path) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\nlanguage = "en"\n', encoding="utf-8")

    config = load_config(config_path)

    assert config.garden_dir == (tmp_path / "garden").resolve()
    assert config.language == "en"


def test_load_config_rejects_missing_language(tmp_path: Path) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\n', encoding="utf-8")

    try:
        load_config(config_path)
    except ValueError as exc:
        assert "language" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
```

- [ ] **Step 2: Write the failing init tests**

```python
from pathlib import Path

from paper_garden.init import ensure_garden


def test_ensure_garden_creates_required_structure(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir)

    assert (garden_dir / "papers").is_dir()
    assert (garden_dir / "tags").is_dir()
    assert (garden_dir / "index.md").is_file()


def test_ensure_garden_is_idempotent(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir)
    ensure_garden(garden_dir)

    assert (garden_dir / "index.md").read_text(encoding="utf-8").startswith("# Paper Garden")
```

- [ ] **Step 3: Run the tests to verify failure**

Run: `uv run pytest tests/test_config.py tests/test_init.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing symbol errors for `paper_garden.config` and `paper_garden.init`

- [ ] **Step 4: Implement config loading**

```python
from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class PaperGardenConfig:
    garden_dir: Path
    language: str


def load_config(config_path: Path) -> PaperGardenConfig:
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing config file: {config_path}")
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    garden_dir = data.get("garden_dir")
    language = data.get("language")
    if not isinstance(garden_dir, str) or not garden_dir.strip():
        raise ValueError("Config field 'garden_dir' must be a non-empty string")
    if not isinstance(language, str) or not language.strip():
        raise ValueError("Config field 'language' must be a non-empty string")
    return PaperGardenConfig(
        garden_dir=(config_path.parent / garden_dir).resolve(),
        language=language.strip(),
    )
```

- [ ] **Step 5: Implement garden initialization**

```python
from pathlib import Path


DEFAULT_INDEX = "# Paper Garden\n\n## Papers\n\n"


def ensure_garden(garden_dir: Path) -> None:
    garden_dir.mkdir(parents=True, exist_ok=True)
    (garden_dir / "papers").mkdir(exist_ok=True)
    (garden_dir / "tags").mkdir(exist_ok=True)
    index_path = garden_dir / "index.md"
    if not index_path.exists():
        index_path.write_text(DEFAULT_INDEX, encoding="utf-8")
```

- [ ] **Step 6: Re-run the tests**

Run: `uv run pytest tests/test_config.py tests/test_init.py -v`
Expected: PASS

- [ ] **Step 7: Commit the config and init work**

```bash
git add src/paper_garden/config.py src/paper_garden/init.py tests/test_config.py tests/test_init.py
git commit -m "feat: add paper garden config and initialization"
```

### Task 3: Implement arXiv Input Normalization And Download

**Files:**
- Create: `src/paper_garden/download.py`
- Create: `tests/test_download.py`

- [ ] **Step 1: Write the failing download tests**

```python
from paper_garden.download import canonical_arxiv_id, build_pdf_url, slugify_title


def test_canonical_arxiv_id_accepts_abs_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/abs/2501.01234") == "2501.01234"


def test_canonical_arxiv_id_accepts_pdf_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/pdf/2501.01234.pdf") == "2501.01234"


def test_build_pdf_url_uses_canonical_id() -> None:
    assert build_pdf_url("2501.01234v2") == "https://arxiv.org/pdf/2501.01234v2.pdf"


def test_slugify_title_is_filesystem_safe() -> None:
    assert slugify_title("A/B Testing: Paper Garden?") == "a_b_testing_paper_garden"
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `uv run pytest tests/test_download.py -v`
Expected: FAIL with missing symbol errors for `paper_garden.download`

- [ ] **Step 3: Implement input normalization helpers**

```python
import re
from urllib.parse import urlparse


SAFE_RE = re.compile(r"[^a-z0-9]+")


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
```

- [ ] **Step 4: Implement metadata fetch and PDF download**

```python
from dataclasses import dataclass
from pathlib import Path
import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class DownloadedPaper:
    arxiv_id: str
    title: str
    paper_slug: str
    pdf_path: Path
    abs_url: str


def fetch_title(session: requests.Session, arxiv_id: str) -> str:
    abs_url = f"https://arxiv.org/abs/{arxiv_id}"
    response = session.get(abs_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.select_one("h1.title")
    text = node.get_text(" ", strip=True) if node else arxiv_id
    return text.split(":", 1)[-1].strip() or arxiv_id


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
```

- [ ] **Step 5: Re-run the tests**

Run: `uv run pytest tests/test_download.py -v`
Expected: PASS

- [ ] **Step 6: Commit the download work**

```bash
git add src/paper_garden/download.py tests/test_download.py
git commit -m "feat: add arxiv normalization and download helpers"
```

### Task 4: Implement Marker Extraction And Wiki Generation

**Files:**
- Create: `src/paper_garden/extract.py`
- Create: `src/paper_garden/wiki.py`
- Create: `templates/wiki.md`

- [ ] **Step 1: Add the wiki template**

```md
# {{ title }}

## Summary
- ...

## Problem
- ...

## Method
- ...

## Results
- ...

## Limitations
- ...

## Terms
- ...
```

- [ ] **Step 2: Implement extraction wrapper**

```python
from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class ExtractionResult:
    markdown_path: Path
    json_path: Path


def run_marker(pdf_path: Path, paper_dir: Path) -> ExtractionResult:
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
    markdown_path = next(extracted_dir.rglob("*.md"))
    json_path = next(extracted_dir.rglob("*.json"))
    return ExtractionResult(markdown_path=markdown_path, json_path=json_path)
```

- [ ] **Step 3: Implement wiki generation**

```python
from pathlib import Path


def build_wiki(title: str, extracted_markdown: str, language: str) -> str:
    heading_map = {
        "en": ("Summary", "Problem", "Method", "Results", "Limitations", "Terms"),
    }
    summary, problem, method, results, limits, terms = heading_map.get(language, heading_map["en"])
    return "\n".join(
        [
            f"# {title}",
            "",
            f"## {summary}",
            "- Generated from extracted paper content.",
            "",
            f"## {problem}",
            "- Fill with durable problem statement from the paper.",
            "",
            f"## {method}",
            "- Fill with the paper's core method.",
            "",
            f"## {results}",
            "- Fill with the main reported findings.",
            "",
            f"## {limits}",
            "- Fill with explicit limitations or caveats.",
            "",
            f"## {terms}",
            "- Add stable terminology here.",
            "",
        ]
    )


def write_wiki(paper_dir: Path, title: str, extracted_markdown: str, language: str) -> Path:
    wiki_path = paper_dir / "wiki.md"
    wiki_path.write_text(build_wiki(title, extracted_markdown, language), encoding="utf-8")
    return wiki_path
```

- [ ] **Step 4: Smoke-test these modules**

Run: `uv run python -c "from pathlib import Path; from paper_garden.wiki import write_wiki; p=Path('tmp_wiki_test'); p.mkdir(exist_ok=True); print(write_wiki(p, 'Test Title', 'body', 'en'))"`
Expected: prints a path ending in `tmp_wiki_test/wiki.md`

- [ ] **Step 5: Commit extraction and wiki generation**

```bash
git add src/paper_garden/extract.py src/paper_garden/wiki.py templates/wiki.md
git commit -m "feat: add marker extraction and wiki generation"
```

### Task 5: Implement Tag And Index Updates

**Files:**
- Create: `src/paper_garden/tags.py`
- Create: `src/paper_garden/index.py`
- Create: `templates/index.md`
- Create: `templates/tag.md`
- Create: `tests/test_tags.py`
- Create: `tests/test_index.py`

- [ ] **Step 1: Write the failing index and tag tests**

```python
from pathlib import Path

from paper_garden.index import update_index
from paper_garden.tags import update_tag_files


def test_update_index_adds_single_entry(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")

    update_index(index_path, "Paper Title", "papers/paper-slug", ["rag", "agents"])

    text = index_path.read_text(encoding="utf-8")
    assert "- [Paper Title](papers/paper-slug/wiki.md) | tags: rag, agents" in text


def test_update_tag_files_creates_one_file_per_tag(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag", "agents"])

    assert (tags_dir / "rag.md").is_file()
    assert (tags_dir / "agents.md").is_file()
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `uv run pytest tests/test_tags.py tests/test_index.py -v`
Expected: FAIL with missing symbol errors for `paper_garden.tags` and `paper_garden.index`

- [ ] **Step 3: Implement index updates**

```python
from pathlib import Path


def update_index(index_path: Path, title: str, paper_rel_dir: str, tags: list[str]) -> None:
    entry = f"- [{title}]({paper_rel_dir}/wiki.md) | tags: {', '.join(tags)}"
    lines = index_path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"- [{title}](")]
    kept.append(entry)
    index_path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
```

- [ ] **Step 4: Implement tag file updates**

```python
from pathlib import Path


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
```

- [ ] **Step 5: Re-run the tests**

Run: `uv run pytest tests/test_tags.py tests/test_index.py -v`
Expected: PASS

- [ ] **Step 6: Commit the index and tag logic**

```bash
git add src/paper_garden/index.py src/paper_garden/tags.py templates/index.md templates/tag.md tests/test_index.py tests/test_tags.py
git commit -m "feat: add paper garden index and tag updates"
```

### Task 6: Wire End-To-End Ingest, Finalize Skill, And Document Usage

**Files:**
- Create: `src/paper_garden/ingest.py`
- Create: `tests/test_ingest.py`
- Modify: `skills/paper-garden/SKILL.md`
- Modify: `skills/paper-garden/scripts/run.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing ingest test**

```python
from pathlib import Path

from paper_garden.ingest import write_metadata


def test_write_metadata_creates_metadata_file(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()

    metadata_path = write_metadata(
        paper_dir=paper_dir,
        arxiv_id="2501.01234",
        title="Paper Title",
        source_url="https://arxiv.org/abs/2501.01234",
        language="en",
        tags=["rag"],
    )

    text = metadata_path.read_text(encoding="utf-8")
    assert 'arxiv_id = "2501.01234"' in text
    assert 'language = "en"' in text
```

- [ ] **Step 2: Run the test to verify failure**

Run: `uv run pytest tests/test_ingest.py -v`
Expected: FAIL with missing symbol errors for `paper_garden.ingest`

- [ ] **Step 3: Implement the ingest orchestrator**

```python
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
    arxiv_id: str,
    title: str,
    source_url: str,
    language: str,
    tags: list[str],
) -> Path:
    metadata_path = paper_dir / "metadata.toml"
    metadata_path.write_text(
        tomli_w.dumps(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "source_url": source_url,
                "language": language,
                "tags": tags,
            }
        ),
        encoding="utf-8",
    )
    return metadata_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest one arXiv paper into Paper Garden.")
    parser.add_argument("input_value")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "skills" / "paper-garden" / "paper_garden.toml"),
    )
    args = parser.parse_args(argv)

    config = load_config(Path(args.config))
    ensure_garden(config.garden_dir)

    with requests.Session() as session:
        paper = download_paper(session, args.input_value, config.garden_dir / "papers")
        extraction = run_marker(paper.pdf_path, paper.pdf_path.parent)
        wiki_path = write_wiki(
            paper.pdf_path.parent,
            paper.title,
            extraction.markdown_path.read_text(encoding="utf-8"),
            config.language,
        )

    tags = ["arxiv"]
    write_metadata(paper.pdf_path.parent, paper.arxiv_id, paper.title, paper.abs_url, config.language, tags)
    paper_rel_dir = f"papers/{paper.paper_slug}"
    update_index(config.garden_dir / "index.md", paper.title, paper_rel_dir, tags)
    update_tag_files(config.garden_dir / "tags", paper.title, paper_rel_dir, tags)

    print(wiki_path)
    return 0
```

- [ ] **Step 4: Update the skill definition to document install-time config**

```md
## Required Configuration

Set these values in `paper_garden.toml` when installing the skill:

- `garden_dir`
- `language`

Defaults:

```toml
garden_dir = "./paper_garden"
language = "en"
```
```

- [ ] **Step 5: Expand the README with a full usage example**

```md
## Install

```bash
uv sync
```

## Skill Configuration

Edit `skills/paper-garden/paper_garden.toml`:

```toml
garden_dir = "./paper_garden"
language = "en"
```

## Example

```bash
uv run python skills/paper-garden/scripts/run.py "https://arxiv.org/abs/2501.01234"
```
```

- [ ] **Step 6: Run the focused tests**

Run: `uv run pytest tests/test_config.py tests/test_init.py tests/test_download.py tests/test_index.py tests/test_tags.py tests/test_ingest.py -v`
Expected: PASS

- [ ] **Step 7: Run a smoke test**

Run: `uv run python skills/paper-garden/scripts/run.py "2501.01234"`
Expected: creates `paper_garden/`, stores one paper under `paper_garden/papers/`, writes `wiki.md`, updates `index.md`, and creates `tags/arxiv.md`

- [ ] **Step 8: Commit the end-to-end workflow**

```bash
git add README.md skills/paper-garden/SKILL.md skills/paper-garden/scripts/run.py src/paper_garden/ingest.py tests/test_ingest.py
git commit -m "feat: wire end-to-end paper ingest workflow"
```

## Self-Review

Spec coverage check:

- Codex skill public entrypoint: covered in Tasks 1 and 6
- skill-level config with `garden_dir` and `language`: covered in Tasks 1, 2, and 6
- one-shot single-paper ingest: covered in Tasks 3, 4, 5, and 6
- garden initialization and structure: covered in Task 2
- index and tag updates: covered in Task 5
- README and public-install guidance: covered in Tasks 1 and 6
- lightweight tests around deterministic modules: covered in Tasks 2, 3, 5, and 6

Placeholder scan:

- No `TODO`, `TBD`, or deferred references remain in implementation steps
- Each code-writing task includes exact file paths and concrete code snippets
- Each verification step includes exact commands and expected outcomes

Type consistency check:

- `load_config()` returns `PaperGardenConfig` and is consumed by `ingest.py`
- `download_paper()` returns `DownloadedPaper` consumed by `ingest.py`
- `run_marker()` returns `ExtractionResult` consumed by `ingest.py`
- `update_index()` and `update_tag_files()` accept the same relative paper directory value
