Ingest a paper into the knowledge garden.

$ARGUMENTS is an arXiv URL, arXiv paper ID, or local PDF path.

## Repo and Config

- Repo root: `__PAPER_GARDEN_REPO__`
- Config: `__PAPER_GARDEN_REPO__/skills/paper-garden/paper_garden.toml`
- All `uv run` commands must run from the repo root.

## First-Time Setup

Read the config file. If it is missing, empty, or has no `garden_dir` / `language` keys:

1. Ask the user: garden directory (default `./paper_garden`) and language (default `en`).
2. Run:

```bash
cd __PAPER_GARDEN_REPO__ && uv run python skills/paper-garden/scripts/configure.py --garden-dir "<choice>" --language "<choice>"
```

3. Confirm the config was written. Do NOT proceed until valid config exists.

## Step 1: Download and Extract

```bash
cd __PAPER_GARDEN_REPO__ && uv run python skills/paper-garden/scripts/download.py "$ARGUMENTS" --config skills/paper-garden/paper_garden.toml
```

The script outputs JSON. Check `duplicate` first:

- **`"duplicate": true`**: Tell the user the title, existing entry, and existing path. Stop here.
- **`"duplicate": false`**: Save all fields (`paper_dir`, `paper_slug`, `title`, `arxiv_id`, `source_kind`, `source_ref`, `extracted_markdown`, `garden_dir`, `language`) for later steps.

## Step 2: Generate Wiki

1. Read the `extracted_markdown` file from Step 1.
2. Write `<paper_dir>/wiki.md` with sections: Summary, Problem, Method, Results, Limitations, Terms.
3. Write in the language from Step 1 config.

## Step 3: Suggest Tags and Summary

1. Suggest 3-7 lowercase hyphenated tags. Check `<garden_dir>/tags/` for existing tags to reuse.
2. Write a one-line summary (max 100 chars) in the configured language. This is immutable after ingest.
3. Present tags and summary to the user. Wait for confirmation before proceeding.

## Step 4: Finalize

```bash
cd __PAPER_GARDEN_REPO__ && uv run python skills/paper-garden/scripts/finalize.py \
  --config skills/paper-garden/paper_garden.toml \
  --paper-dir "<paper_dir>" \
  --title "<title>" \
  --paper-slug "<paper_slug>" \
  --tags "<tag1,tag2,tag3>" \
  --summary "<one-line summary>" \
  --source-ref "<source_ref>" \
  --source-kind "<source_kind>" \
  --arxiv-id "<arxiv_id>"
```

Omit `--arxiv-id` if the source is a local PDF.

## Step 5: Report

Tell the user: paper directory, wiki path, final tags, updated index and tag files.
