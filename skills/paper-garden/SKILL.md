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

The script outputs JSON. Check the `duplicate` field first:

**If `"duplicate": true`:**
The paper already exists in the garden. Tell the user:
- The paper title
- The existing entry from index.md
- The path to the existing paper directory and wiki
- **Stop here. Do NOT proceed to Step 2.**

**If `"duplicate": false`:**
Save all fields — you need them for later steps:
- `paper_dir`, `paper_slug`, `title`, `arxiv_id`, `source_kind`, `source_ref`
- `year`, `needs_year`
- `extracted_markdown` — path to the extracted markdown file
- `garden_dir`, `language`

**If `"needs_year": true`** (local PDF, or year not derivable from arXiv ID):
Ask the user: "What year was this paper published? (YYYY)"
Save the answer and pass it to `finalize.py` as `--year`.

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

### Step 3: Suggest Tags, Summary, and Confirm

1. Based on the paper content, suggest **3-7 tags**. Guidelines:
   - Lowercase, hyphenated (e.g., `retrieval-augmented-generation`, `transformer`)
   - Mix of topic tags (e.g., `large-language-model`, `computer-vision`) and method tags (e.g., `fine-tuning`, `distillation`)
   - Check `<garden_dir>/tags/` for existing tag files — reuse existing tags when the paper fits
2. Write a **one-line summary** of the paper (max 100 characters), in the configured language. This summary appears in index.md and tag files alongside the paper link. **The summary is immutable once written — it will never be modified after ingest.** Take extra care to make it accurate and capture the paper's core contribution.
3. Present suggested tags and summary to the user.
4. Wait for the user to confirm, add, remove, or rename tags, and approve the summary.

**Do NOT proceed until the user confirms the final tag list and summary.**

### Step 4: Finalize

Run with the confirmed tags and summary:

```bash
uv run python skills/paper-garden/scripts/finalize.py \
  --config skills/paper-garden/paper_garden.toml \
  --paper-dir "<paper_dir>" \
  --title "<title>" \
  --paper-slug "<paper_slug>" \
  --tags "<tag1,tag2,tag3>" \
  --summary "<one-line summary>" \
  --year "<YYYY>" \
  --source-ref "<source_ref>" \
  --source-kind "<source_kind>" \
  --arxiv-id "<arxiv_id>"
```

- Omit `--arxiv-id` if the source is a local PDF.
- `--year` is required when source is local PDF. For arXiv sources, it can be omitted and will be derived from the arXiv ID.

The script prints the assigned paper ID (`pg-<year>-<hex5>`).

### Step 5: Report

Tell the user:
- Paper directory path
- Wiki file path
- Assigned paper ID (from `finalize.py` output)
- Final confirmed tags
- Which index and tag files were updated
