---
name: paper-garden
description: Ingest one arXiv paper or local PDF into a Markdown knowledge garden with LLM-generated wiki and user-confirmed tags.
---

# Paper Garden

Use this skill when the user wants to ingest a paper into their knowledge garden.

## Prerequisites

This skill requires running from the paper-garden repository root. All commands use `uv run` which resolves dependencies from `pyproject.toml`.

If the repo is not already cloned, instruct the user to:

```bash
git clone https://github.com/<owner>/paper-garden.git
cd paper-garden
```

All commands below assume the working directory is the repo root.

## First-Time Setup

Before running the workflow, read `skills/paper-garden/paper_garden.toml`.

If the file is missing, empty, or contains only comments (no `garden_dir` or `language` keys), you MUST configure it before proceeding:

1. Ask the user two questions:
   - **Garden directory**: Where should papers be stored? Default: `./paper_garden`
   - **Language**: What language for generated wiki content? Default: `en`
2. After the user answers, write the config:

```bash
uv run python skills/paper-garden/scripts/configure.py --garden-dir "<user_choice>" --language "<user_choice>"
```

3. Confirm the config was written by reading the file again.

**Do NOT proceed with ingest until valid configuration exists.**

## Ingest Workflow

### Step 1: Download and Extract

Run:

```bash
uv run python skills/paper-garden/scripts/download.py "<input>" --config skills/paper-garden/paper_garden.toml
```

Where `<input>` is an arXiv abs/html/pdf URL, arXiv paper ID, or local PDF path.

The script outputs JSON. Save all fields — you need them for later steps:
- `paper_dir`, `paper_slug`, `title`, `arxiv_id`, `source_kind`, `source_ref`
- `extracted_markdown` — path to the extracted markdown file
- `garden_dir`, `language`

### Step 2: Generate Wiki

1. Read the extracted markdown file (the `extracted_markdown` path from Step 1).
2. Analyze the paper content thoroughly.
3. Write `<paper_dir>/wiki.md` with these sections:

```markdown
# <Paper Title>

## Summary
3-5 bullet points of key contributions.

## Problem
What problem does the paper address? Why does it matter?

## Method
Core approach, technique, or architecture.

## Results
Main findings, metrics, and comparisons.

## Limitations
Stated or apparent limitations and caveats.

## Terms
Key terminology defined or used in the paper.
```

Write in the language specified by `language` from Step 1. Use the Write tool to create the file.

### Step 3: Suggest and Confirm Tags

1. Based on the paper content, suggest **3-7 tags**. Guidelines:
   - Lowercase, hyphenated (e.g., `retrieval-augmented-generation`, `transformer`)
   - Mix of topic tags (e.g., `large-language-model`, `computer-vision`) and method tags (e.g., `fine-tuning`, `distillation`)
   - Check `<garden_dir>/tags/` for existing tag files — reuse existing tags when the paper fits
2. Present suggested tags to the user.
3. Wait for the user to confirm, add, remove, or rename tags.

**Do NOT proceed until the user confirms the final tag list.**

### Step 4: Finalize

Run with the confirmed tags:

```bash
uv run python skills/paper-garden/scripts/finalize.py \
  --config skills/paper-garden/paper_garden.toml \
  --paper-dir "<paper_dir>" \
  --title "<title>" \
  --paper-slug "<paper_slug>" \
  --tags "<tag1,tag2,tag3>" \
  --source-ref "<source_ref>" \
  --source-kind "<source_kind>" \
  --arxiv-id "<arxiv_id>"
```

Omit `--arxiv-id` if the source is a local PDF.

### Step 5: Report

Tell the user:
- Paper directory path
- Wiki file path
- Final confirmed tags
- Which index and tag files were updated
