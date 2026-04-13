---
name: paper-garden
description: Ingest one arXiv paper or local PDF into the configured Markdown paper garden.
---

# Paper Garden

Use this skill when the user wants to ingest a single arXiv paper or local PDF into the configured garden.

## Required Configuration

Set these values in `paper_garden.toml` when installing the skill:

- `garden_dir`
- `language`

Defaults:

```toml
garden_dir = "./paper_garden"
language = "en"
```

## Workflow

1. Read `paper_garden.toml` from this skill directory.
2. Run:

```bash
uv run python skills/paper-garden/scripts/run.py "<arxiv_url_or_id_or_local_pdf>"
```

3. Report the created paper directory, wiki path, and updated index files.

## Notes

- `garden_dir` is resolved from the current working directory, not from the skill directory
- `language` only controls content generation behavior
- current source support is arXiv inputs and local PDF files
