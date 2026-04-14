Read one or more papers from the knowledge garden by their IDs and answer a question.

`$ARGUMENTS` is `<paper_id> [<paper_id> ...] <question>`. Examples:

- Single: `pg-2024-00005 What kernel does the paper use?`
- Multiple: `pg-2024-00005 pg-2023-00008 Compare their assumptions about order flow.`

Parse: split on whitespace; consume leading tokens matching `^pg-\d{4}-[0-9a-f]{5}$` as the paper ID list; the remainder joined with single spaces is the question. At least one ID is required.

## Repo and Config

- Repo root: `__PAPER_GARDEN_REPO__`
- Config: `__PAPER_GARDEN_REPO__/skills/paper-garden/paper_garden.toml` (shared with `/paper-garden`)
- All `uv run` commands must run from the repo root.

## Step 1: Locate (per ID)

For **each** parsed ID:

```bash
cd __PAPER_GARDEN_REPO__ && uv run python skills/paper-read/scripts/locate.py "<paper_id>" --config skills/paper-garden/paper_garden.toml
```

- Non-zero exit → tell the user `paper id '<paper_id>' not found — check spelling or that ingest completed`. If some IDs resolved and others failed, report which failed and ask whether to proceed with the resolved subset or stop.
- Success → save JSON fields `paper_dir`, `wiki_path`, `extracted_markdown`, `title`, `tags`, `year`.

Keep resolved papers in a list, preserving user-given order.

## Step 2: Read each wiki

Read every resolved `wiki_path` in full. Mandatory and cheap.

## Step 3: Answer or escalate

- Wikis answer the question → respond directly, citing sections and noting which paper each point came from.
- Some wiki insufficient → read that paper's `extracted_markdown`. Use `grep` or section anchors. Read only what you need. Only escalate for papers that need it — do not read every paper's full text.
- `extracted_markdown` missing → tell the user extraction was skipped for that paper; offer to re-run `/paper-garden`.

## Step 4: Optional wiki update (patch flow)

If you notice a factual error or meaningful gap in a paper's wiki relevant to the question:

1. Identify the exact snippet in that `wiki.md`.
2. Draft a replacement.
3. Show original and replacement side by side and ask `Apply? (yes / edit / skip)`.
4. On `yes`, apply with the `Edit` tool using the exact original as `old_string`. Do not rewrite the whole wiki. Do not auto-apply. Confirm each paper's update separately — do not batch.

## Step 5: Report

For each paper, summarize: title and ID, what was read (wiki only, or wiki + full-text sections), and any wiki updates applied with their path.
