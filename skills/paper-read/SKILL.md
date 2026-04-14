---
name: paper-read
description: Read one or more papers from the garden by their pg-YYYY-xxxxx IDs. Answer questions using the wiki first, then extracted full text as needed. Optionally propose wiki patches.
---

# Paper Read

Use this skill when the user wants to ask a question about one or more specific papers already ingested into the Paper Garden.

`$ARGUMENTS` is `<paper_id> [<paper_id> ...] <question>`. Examples:

- Single: `pg-2024-00005 What kernel does the paper use?`
- Multiple: `pg-2024-00005 pg-2023-00008 Compare their assumptions about order flow.`

Parse `$ARGUMENTS` as follows: split on whitespace; consume leading tokens that match `^pg-\d{4}-[0-9a-f]{5}$` as the paper ID list; the remainder (joined with single spaces) is the question. At least one ID is required.

## Prerequisites

Run from the paper-garden repository root. Shared configuration lives at `skills/paper-garden/paper_garden.toml` (same file used by the `paper-garden` ingest skill).

## Workflow

### Step 1: Locate (per ID)

For **each** parsed paper ID, run:

```bash
uv run python skills/paper-read/scripts/locate.py <paper_id> --config skills/paper-garden/paper_garden.toml
```

- **Non-zero exit for any ID:** tell the user `paper id '<paper_id>' not found — check spelling or that ingest completed`. If some IDs resolved and others failed, report which failed and ask whether to proceed with the resolved subset or stop.
- **Success:** the script prints JSON. Save `paper_dir`, `wiki_path`, `extracted_markdown`, `title`, `tags`, `year` for that ID.

Keep the resolved papers in a list, preserving the order the user gave.

### Step 2: Read each wiki

For each resolved paper, read its `wiki_path` in full. This is mandatory and cheap. Do not skip to full text.

### Step 3: Answer or escalate

- **If the wikis together answer the question:** respond directly, citing the relevant sections and noting which paper each point came from (use title or ID).
- **If a wiki is insufficient for the part of the question that concerns that paper:** read its `extracted_markdown`.
  - For long papers, use `grep` or section anchors to find relevant passages instead of reading the whole file.
  - Read only the sections you need. Stop reading once you have enough to answer.
  - Only escalate to full text for papers that actually need it — do not read every paper's full text unless the question requires it.
- **If `extracted_markdown` is missing on disk:** tell the user that paper was ingested without extraction and offer to re-run `/paper-garden` on its source.

### Step 4: Optional wiki update (patch flow)

While reading a full text, if you notice a factual error or a meaningful gap in **that paper's** wiki relevant to the user's question:

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

Confirm each update separately — do not batch multiple patches across papers into one confirmation.

### Step 5: Report

For each paper, summarize:
- Title and ID
- What was read (wiki only, or wiki + full-text sections X/Y)
- Any wiki updates applied, with the `wiki_path`
