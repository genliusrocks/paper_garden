# Paper Read Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `paper-read` skill and `/paper-read` command that, given a `pg-YYYY-xxxxx` ID and a question, locates the paper, reads the wiki, and (if needed) reads the extracted full text, with an optional patch-based wiki update flow.

**Architecture:** A new `paper_garden.locate` module resolves an ID to filesystem paths (index.md first, metadata.toml fallback). A thin CLI wraps it and emits JSON. Skill/command markdown documents the agent workflow. Reuses existing `config.py`, `ids.py`, and `paper_garden.toml`.

**Tech Stack:** Python 3.12, pytest, tomllib, existing paper_garden package.

**Repo root:** `/home/wesley/ws/paper_garden`

**Spec:** `docs/superpowers/specs/2026-04-14-paper-read-design.md`

---

## File Structure

**Created:**
- `src/paper_garden/locate.py` — `LocatedPaper` dataclass, `locate()` function
- `skills/paper-read/SKILL.md` — Codex skill entry
- `skills/paper-read/scripts/locate.py` — thin CLI wrapping `paper_garden.locate`
- `commands/paper-read.md` — Claude Code command (uses `__PAPER_GARDEN_REPO__` placeholder)
- `tests/test_locate.py` — unit tests for the locate module

**Modified:**
- `tests/test_skill_bundle.py` — assertions extended to cover `skills/paper-read/`
- `README.md` — add `cp commands/paper-read.md ~/.claude/commands/...` install step

---

## Task 1: Create `locate.py` with `LocatedPaper` dataclass and index-based lookup

**Files:**
- Create: `src/paper_garden/locate.py`
- Test: `tests/test_locate.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_locate.py
from pathlib import Path

import tomli_w

from paper_garden.locate import LocatedPaper, locate


def _make_garden(tmp_path: Path) -> Path:
    garden = tmp_path / "garden"
    (garden / "papers" / "2408.03594_sample").mkdir(parents=True)
    (garden / "tags").mkdir()
    (garden / "index.md").write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- `pg-2024-00001` [Sample Paper](papers/2408.03594_sample/wiki.md) | tags: a, b — one-line summary\n",
        encoding="utf-8",
    )
    (garden / "papers" / "2408.03594_sample" / "metadata.toml").write_text(
        tomli_w.dumps({
            "id": "pg-2024-00001",
            "year": "2024",
            "title": "Sample Paper",
            "source_ref": "https://arxiv.org/abs/2408.03594",
            "source_kind": "arxiv",
            "language": "en",
            "tags": ["a", "b"],
            "arxiv_id": "2408.03594",
        }),
        encoding="utf-8",
    )
    return garden


def test_locate_finds_paper_via_index(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    result = locate(garden, "pg-2024-00001")
    assert isinstance(result, LocatedPaper)
    assert result.paper_id == "pg-2024-00001"
    assert result.paper_dir == garden / "papers" / "2408.03594_sample"
    assert result.wiki_path == garden / "papers" / "2408.03594_sample" / "wiki.md"
    assert result.extracted_markdown == garden / "papers" / "2408.03594_sample" / "extracted" / "document.md"
    assert result.title == "Sample Paper"
    assert result.tags == ["a", "b"]
    assert result.year == "2024"


def test_locate_returns_none_when_not_found(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    assert locate(garden, "pg-2024-99999") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_locate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'paper_garden.locate'`

- [ ] **Step 3: Create `src/paper_garden/locate.py`**

```python
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


def locate(garden_dir: Path, paper_id: str) -> LocatedPaper | None:
    return _locate_via_index(garden_dir, paper_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_locate.py -v`
Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add src/paper_garden/locate.py tests/test_locate.py
git commit -m "feat: add locate module with index-based lookup"
```

---

## Task 2: Add metadata.toml fallback to `locate()`

**Files:**
- Modify: `src/paper_garden/locate.py`
- Test: `tests/test_locate.py`

- [ ] **Step 1: Add a failing test**

Append to `tests/test_locate.py`:

```python
def test_locate_falls_back_to_metadata_when_index_missing_id(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    # Simulate index drift: overwrite index.md without the ID line
    (garden / "index.md").write_text(
        "# Paper Garden\n\n## Papers\n\n", encoding="utf-8"
    )
    result = locate(garden, "pg-2024-00001")
    assert result is not None
    assert result.paper_id == "pg-2024-00001"
    assert result.paper_dir == garden / "papers" / "2408.03594_sample"
    assert result.title == "Sample Paper"


def test_locate_returns_none_when_metadata_missing_id_field(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    (garden / "index.md").write_text("# Paper Garden\n\n", encoding="utf-8")
    # Overwrite metadata.toml without id field
    import tomli_w
    (garden / "papers" / "2408.03594_sample" / "metadata.toml").write_text(
        tomli_w.dumps({"title": "Sample Paper", "tags": [], "year": "2024"}),
        encoding="utf-8",
    )
    assert locate(garden, "pg-2024-00001") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_locate.py -v`
Expected: `test_locate_falls_back_to_metadata_when_index_missing_id` FAILS (returns None)

- [ ] **Step 3: Add fallback to `locate()`**

Replace the `locate` function in `src/paper_garden/locate.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_locate.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add src/paper_garden/locate.py tests/test_locate.py
git commit -m "feat: add metadata fallback to locate()"
```

---

## Task 3: Create the `skills/paper-read/scripts/locate.py` CLI

**Files:**
- Create: `skills/paper-read/scripts/locate.py`

- [ ] **Step 1: Create the CLI script**

```python
# skills/paper-read/scripts/locate.py
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
```

- [ ] **Step 2: Verify syntax**

Run: `cd /home/wesley/ws/paper_garden && uv run python -c "import ast; ast.parse(open('skills/paper-read/scripts/locate.py').read())"`
Expected: no output

- [ ] **Step 3: Smoke test against the real garden**

Run: `cd /home/wesley/ws/paper_garden && uv run python skills/paper-read/scripts/locate.py pg-2024-00005 --config skills/paper-garden/paper_garden.toml`
Expected: JSON with `paper_dir` pointing to the Forecasting HFT OFI paper, exit 0.

Run: `cd /home/wesley/ws/paper_garden && uv run python skills/paper-read/scripts/locate.py pg-2024-99999 --config skills/paper-garden/paper_garden.toml`
Expected: stderr `paper id 'pg-2024-99999' not found`, exit 1.

- [ ] **Step 4: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add skills/paper-read/scripts/locate.py
git commit -m "feat: add paper-read locate CLI"
```

---

## Task 4: Extend `test_skill_bundle.py` to cover `paper-read`

**Files:**
- Modify: `tests/test_skill_bundle.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_skill_bundle.py`:

```python
def test_paper_read_scripts_import_from_package() -> None:
    scripts_dir = Path("skills/paper-read/scripts")
    assert scripts_dir.is_dir(), "skills/paper-read/scripts must exist"
    for script in scripts_dir.glob("*.py"):
        text = script.read_text(encoding="utf-8")
        assert "from paper_garden" in text or script.name == "__init__.py", (
            f"{script.name} does not import from paper_garden package"
        )


def test_paper_read_skill_md_references_locate_script() -> None:
    skill_md = Path("skills/paper-read/SKILL.md").read_text(encoding="utf-8")
    assert "locate.py" in skill_md
    assert "$ARGUMENTS" in skill_md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_skill_bundle.py -v`
Expected: `test_paper_read_skill_md_references_locate_script` FAILS (SKILL.md missing). `test_paper_read_scripts_import_from_package` PASSES because the CLI from Task 3 already satisfies it.

- [ ] **Step 3: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add tests/test_skill_bundle.py
git commit -m "test: cover paper-read skill bundle structure"
```

---

## Task 5: Create `skills/paper-read/SKILL.md`

**Files:**
- Create: `skills/paper-read/SKILL.md`

- [ ] **Step 1: Write `skills/paper-read/SKILL.md`**

```markdown
---
name: paper-read
description: Read a paper from the garden by its pg-YYYY-xxxxx ID. Answer questions using the wiki first, then extracted full text as needed. Optionally propose wiki patches.
---

# Paper Read

Use this skill when the user wants to ask a question about a specific paper already ingested into the Paper Garden.

`$ARGUMENTS` is `<paper_id> <question>`, for example: `pg-2024-00005 What kernel does the paper use?`

Split `$ARGUMENTS` on the first whitespace: the first token is the paper ID, the rest is the question.

## Prerequisites

Run from the paper-garden repository root. Shared configuration lives at `skills/paper-garden/paper_garden.toml` (same file used by the `paper-garden` ingest skill).

## Workflow

### Step 1: Locate

Run:

```bash
uv run python skills/paper-read/scripts/locate.py <paper_id> --config skills/paper-garden/paper_garden.toml
```

- **Non-zero exit:** tell the user `paper id '<paper_id>' not found — check spelling or that ingest completed` and stop.
- **Success:** the script prints JSON. Save `paper_dir`, `wiki_path`, `extracted_markdown`, `title`, `tags`, `year`.

### Step 2: Read the wiki

Read `wiki_path` in full. This is mandatory and cheap. Do not skip to the full text.

### Step 3: Answer or escalate

- **If the wiki answers the question:** respond directly, citing the relevant wiki sections.
- **If the wiki is not sufficient:** read `extracted_markdown`.
  - For long papers, use `grep` or section anchors to find relevant passages instead of reading the whole file.
  - Read only the sections you need. Stop reading once you have enough to answer.
- **If `extracted_markdown` is missing on disk:** tell the user the paper was ingested without extraction and offer to re-run `/paper-garden` on the source.

### Step 4: Optional wiki update (patch flow)

While reading the full text, if you notice a factual error or a meaningful gap in the wiki that is relevant to the user's question:

1. Identify the exact snippet in `wiki.md` that is wrong or incomplete.
2. Draft a replacement snippet.
3. Present both to the user side by side:

   ```
   Proposed wiki update in <wiki_path>:

   - Original:
     <exact original text>

   + Replacement:
     <proposed replacement>

   Apply? (yes / edit / skip)
   ```

4. On `yes`, apply the change with the `Edit` tool using the exact original text as `old_string` and the replacement as `new_string`. Do NOT rewrite the whole wiki. Do NOT apply without explicit confirmation.
5. On `edit`, let the user amend the replacement, then re-confirm.
6. On `skip`, proceed without changes.

Never auto-apply. Never chain multiple updates in one confirmation.

### Step 5: Report

Summarize:
- Paper title and ID
- What was read (wiki only, or wiki + full-text sections X/Y)
- Any wiki updates applied, with the `wiki_path`
```

- [ ] **Step 2: Run skill bundle tests**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/test_skill_bundle.py -v`
Expected: all PASS.

- [ ] **Step 3: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add skills/paper-read/SKILL.md
git commit -m "feat: add paper-read SKILL.md"
```

---

## Task 6: Create `commands/paper-read.md` for Claude Code

**Files:**
- Create: `commands/paper-read.md`

- [ ] **Step 1: Write `commands/paper-read.md`**

```markdown
Read a paper from the knowledge garden by its ID and answer a question.

`$ARGUMENTS` is `<paper_id> <question>`, for example: `pg-2024-00005 What kernel does the paper use?`

Split `$ARGUMENTS` on the first whitespace: the first token is the paper ID, the rest is the question.

## Repo and Config

- Repo root: `__PAPER_GARDEN_REPO__`
- Config: `__PAPER_GARDEN_REPO__/skills/paper-garden/paper_garden.toml` (shared with `/paper-garden`)
- All `uv run` commands must run from the repo root.

## Step 1: Locate

```bash
cd __PAPER_GARDEN_REPO__ && uv run python skills/paper-read/scripts/locate.py "<paper_id>" --config skills/paper-garden/paper_garden.toml
```

- Non-zero exit → tell the user `paper id '<paper_id>' not found — check spelling or that ingest completed` and stop.
- Success → save JSON fields `paper_dir`, `wiki_path`, `extracted_markdown`, `title`, `tags`, `year`.

## Step 2: Read the wiki

Read `wiki_path` in full. Mandatory and cheap.

## Step 3: Answer or escalate

- Wiki answers the question → respond directly, citing wiki sections.
- Wiki insufficient → read `extracted_markdown`. Use `grep` or section anchors to find relevant passages. Read only what you need.
- `extracted_markdown` missing → tell the user extraction was skipped; offer to re-run `/paper-garden`.

## Step 4: Optional wiki update (patch flow)

If you notice a factual error or meaningful gap in the wiki relevant to the question:

1. Identify the exact snippet in `wiki.md` that is wrong or incomplete.
2. Draft a replacement snippet.
3. Show the user the original and the replacement side by side and ask `Apply? (yes / edit / skip)`.
4. On `yes`, apply with the `Edit` tool using the exact original as `old_string`. Do not rewrite the whole wiki. Do not auto-apply.

## Step 5: Report

Summarize: paper title and ID, what was read (wiki only, or wiki + full-text sections), and any wiki updates applied with their path.
```

- [ ] **Step 2: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add commands/paper-read.md
git commit -m "feat: add /paper-read Claude Code command"
```

---

## Task 7: Document install in README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current install section**

Run: `cd /home/wesley/ws/paper_garden && grep -n "paper-garden.md" README.md`

Expected: one block that copies `commands/paper-garden.md` and runs `sed`.

- [ ] **Step 2: Add the paper-read install lines**

In `README.md`, find the block:

```bash
cp commands/paper-garden.md ~/.claude/commands/paper-garden.md
sed -i "s|__PAPER_GARDEN_REPO__|$(pwd)|g" ~/.claude/commands/paper-garden.md
```

Extend it to:

```bash
cp commands/paper-garden.md ~/.claude/commands/paper-garden.md
cp commands/paper-read.md ~/.claude/commands/paper-read.md
sed -i "s|__PAPER_GARDEN_REPO__|$(pwd)|g" ~/.claude/commands/paper-garden.md ~/.claude/commands/paper-read.md
```

Use `Edit` with the old block as `old_string` and the new block as `new_string`.

- [ ] **Step 3: Commit**

```bash
cd /home/wesley/ws/paper_garden
git add README.md
git commit -m "docs: document /paper-read install"
```

---

## Task 8: Install `/paper-read` locally and smoke-test

**Files:** none (local install only)

- [ ] **Step 1: Install the command**

```bash
cp /home/wesley/ws/paper_garden/commands/paper-read.md ~/.claude/commands/paper-read.md
sed -i "s|__PAPER_GARDEN_REPO__|/home/wesley/ws/paper_garden|g" ~/.claude/commands/paper-read.md
```

- [ ] **Step 2: Verify the placeholder was replaced**

Run: `grep -c __PAPER_GARDEN_REPO__ ~/.claude/commands/paper-read.md`
Expected: `0`

- [ ] **Step 3: Smoke-test the locate CLI against the real garden**

Run:

```bash
cd /home/wesley/ws/paper_garden && uv run python skills/paper-read/scripts/locate.py pg-2024-00005 --config skills/paper-garden/paper_garden.toml
```

Expected: JSON with `title` containing "Forecasting High Frequency Order Flow Imbalance" and `paper_dir` ending in `2408.03594v1_...`.

---

## Task 9: Final verification

- [ ] **Step 1: Full test suite**

Run: `cd /home/wesley/ws/paper_garden && uv run pytest tests/ -v`
Expected: all PASS. New: `tests/test_locate.py` (4), plus 2 new assertions in `test_skill_bundle.py`.

- [ ] **Step 2: Confirm file inventory**

Run:

```bash
cd /home/wesley/ws/paper_garden && ls skills/paper-read/ skills/paper-read/scripts/ commands/
```

Expected:
- `skills/paper-read/SKILL.md`
- `skills/paper-read/scripts/locate.py`
- `commands/paper-read.md` (alongside `commands/paper-garden.md`)

- [ ] **Step 3: Commit anything lingering**

```bash
cd /home/wesley/ws/paper_garden
git status
```

If anything remains uncommitted, commit it. Otherwise done.
