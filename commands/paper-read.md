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
