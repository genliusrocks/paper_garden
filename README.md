# Paper Garden

Paper Garden is a Codex skill and Claude Code command for ingesting papers into a Markdown-based knowledge garden.

## What It Does

Given one arXiv URL, arXiv id, or local PDF path, Paper Garden:

- downloads or copies the PDF
- extracts Markdown and JSON with `marker`
- writes a reusable `wiki.md`
- updates `index.md`
- updates tag index files

## Requirements

- Python 3.12+
- `uv`

## Install

```bash
uv sync --extra dev
```

## Configure

After installing the skill, initialize its config:

```bash
uv run python skills/paper-garden/scripts/configure.py --garden-dir "./paper_garden" --language "en"
```

If you omit either option, the script uses these defaults:

```toml
garden_dir = "./paper_garden"
language = "en"
```

Notes:

- `garden_dir` is resolved relative to the current working directory when the skill runs
- `language` is passed through to the content-generation layer; file structure remains stable
- if configuration is missing, Paper Garden refuses to run and points you to `configure.py`

## Example

```bash
uv run python skills/paper-garden/scripts/run.py "https://arxiv.org/abs/2501.01234"
```

```bash
uv run python skills/paper-garden/scripts/run.py "/path/to/paper.pdf"
```

Expected output structure:

```text
paper_garden/
  index.md
  papers/
    <paper_slug>/
      paper.pdf
      extracted/
        document.md
        document.json
      wiki.md
      metadata.toml
  tags/
    <tag>.md
```

## Status

Current input support:

- arXiv `abs` / `html` / `pdf` URLs
- arXiv paper ids
- local PDF files

Planned later:

- additional paper URLs beyond arXiv
