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
