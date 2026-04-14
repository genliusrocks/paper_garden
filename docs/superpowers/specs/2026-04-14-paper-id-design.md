# Paper ID Design

**Date:** 2026-04-14
**Status:** Approved, pending implementation plan

## Purpose

Give every paper a short, stable identifier so that future MCP tools (and humans) can reference papers by a compact ID instead of by full title or directory slug.

## ID Format

`pg-<year>-<hex5>`

- `year`: 4-digit publication year of the paper
- `hex5`: globally-incrementing counter, 5-digit lowercase hexadecimal, zero-padded
- Examples: `pg-2017-00001`, `pg-2024-00a3f`, `pg-2003-1b2c4`
- Capacity: 16^5 = 1,048,576 papers

### Year Source

Priority:
1. arXiv papers: derived from `arxiv_id` via existing `year_from_arxiv_id()`
2. Local PDFs or arXiv papers where year cannot be inferred: **block and ask the user**

The current year is never a silent fallback. If year cannot be determined programmatically, the agent must stop and request it.

### Counter Rules

- `hex5` is a single global counter, shared across all years
- Next value = `max(existing hex5) + 1`
- Counters are never reused. If a paper is deleted, its ID is retired.
- Papers are not re-ordered by year; the counter reflects ingestion order.

### Immutability

Once written to `metadata.toml`, a paper's ID is permanent. It is the canonical reference and must survive title changes, re-tagging, and wiki edits.

## Storage

IDs are written to three locations:

### 1. `metadata.toml` (authoritative)

New fields:
```toml
id = "pg-2024-00a3f"
year = "2024"
```

This is the source of truth. Other files display the ID but do not own it.

### 2. `index.md`

Replaces the current `(YYYY)` prefix. New format:

```
- `pg-2024-00a3f` [Forecasting High Frequency Order Flow Imbalance](papers/<slug>/wiki.md) | tags: ... — summary
```

Year is no longer displayed separately since the ID contains it.

### 3. `tags/*.md`

Same pattern:

```
- `pg-2024-00a3f` [Forecasting High Frequency Order Flow Imbalance](papers/<slug>/wiki.md) — summary
```

### Not Stored In

- `wiki.md`: wiki is content-layer, ID is index-layer. Kept clean.

## Components

### New: `src/paper_garden/ids.py`

Single responsibility: generate and parse paper IDs.

- `ID_RE = re.compile(r"^- `pg-(\d{4})-([0-9a-f]{5})`")` — matches an ID-prefixed index/tag line
- `parse_existing_seqs(index_path: Path) -> list[int]` — returns decimal values of all hex5 sequences found
- `next_id(index_path: Path, year: str) -> str` — computes `f"pg-{year}-{next_seq:05x}"` where `next_seq = max(parse_existing_seqs(...), default=0) + 1`

### Modified: `src/paper_garden/download.py`

`ResolvedPaper` gains a `year: str | None` field, populated by `year_from_arxiv_id()`.

### Modified: `skills/paper-garden/scripts/download.py`

Output JSON gains `year` and `needs_year` fields:
- If `year` was resolved: `{"year": "2024", "needs_year": false}`
- If not: `{"year": null, "needs_year": true}` — agent stops and asks user

### Modified: `skills/paper-garden/scripts/finalize.py`

- New required arg: `--year`
- Generates ID via `ids.next_id(index_path, year)` before writing anything
- Writes `id` and `year` to `metadata.toml`
- Passes `paper_id` to `update_index()` and `update_tag_files()`

### Modified: `src/paper_garden/index.py` and `src/paper_garden/tags.py`

- `update_index(..., paper_id: str, ...)` — new required parameter
- `update_tag_files(..., paper_id: str, ...)` — new required parameter
- Entry format changed: `- \`{id}\` [{title}]({link}) ...`
- **Deduplication key changes from normalized title to paper_id.** Lines are matched by extracting the ID via `ID_RE`. This is more reliable than title matching.
- `year` parameter is removed (the ID now carries it).

### New: `skills/paper-garden/scripts/migrate_ids.py`

One-shot migration for gardens created before this feature.

Behavior:
1. Read `<garden_dir>/index.md`, iterate paper entries in current order
2. For each paper:
   - Read `<paper_dir>/metadata.toml` to get `arxiv_id`
   - Derive year via `year_from_arxiv_id()`; if unavailable, prompt user interactively
   - Skip if `metadata.toml` already has `id` field (idempotent)
   - Assign next sequence in current order: `00001`, `00002`, ...
3. Update `metadata.toml` (add `id`, `year` fields)
4. Rewrite `index.md` entry with new format
5. Rewrite every tag file that references this paper

## Data Flow

### New ingest (arXiv, year known)

```
download.py → resolves year from arxiv_id → outputs JSON with year
  ↓
agent generates wiki, gets tag/summary confirmation from user
  ↓
finalize.py --year 2024 → ids.next_id() → writes metadata.toml, index.md, tag files
```

### New ingest (local PDF, year unknown)

```
download.py → needs_year=true → agent stops, asks user "What year was this paper published?"
  ↓
user answers 2023
  ↓
finalize.py --year 2023 → ...
```

### Migration

```
migrate_ids.py → reads index.md in order → for each paper → asks year if needed
  → writes id to metadata.toml → rewrites index.md and tags/*.md
```

## Error Handling

- **Duplicate ID in index.md:** should never happen (counter is monotonic), but if detected, abort and report.
- **`metadata.toml` missing during migration:** abort with clear message; do not silently create.
- **Invalid year from user:** reject anything that isn't a 4-digit year between 1900 and current year + 1.
- **Malformed existing IDs during parse:** ignored (the regex won't match); counter proceeds from the valid ones.

## Testing

### New: `tests/test_ids.py`

- `test_parse_existing_seqs_empty`
- `test_parse_existing_seqs_extracts_hex5_values`
- `test_parse_existing_seqs_ignores_malformed_lines`
- `test_next_id_starts_at_00001`
- `test_next_id_increments_from_max`
- `test_next_id_handles_mixed_years` — confirms global counter, not per-year

### Updated: `tests/test_index.py`

- Entry format now `\`{id}\` [{title}](...)`
- Dedup by `paper_id`, not normalized title
- Year no longer in entry (carried by ID)

### Updated: `tests/test_tags.py`

Same changes as `test_index.py`.

### Updated: `tests/test_ingest.py`

- End-to-end test passes `--year`
- `metadata.toml` assertion includes `id` and `year`

### New: `tests/test_migrate.py`

- Migration assigns sequential IDs in index order
- Migration is idempotent (second run is a no-op)
- Migration updates all three locations (metadata, index, tags)

## Out of Scope

- MCP tool itself (this spec only makes IDs available; the MCP is a separate project)
- Cross-garden ID namespacing (each garden has its own counter)
- Human-chosen custom IDs
- ID rendering in `wiki.md`

## Non-Goals

- Not a BibTeX citation key replacement
- Not a content-addressable hash (IDs are allocated, not derived)
- Not intended for sharing across users (each garden's sequence is local)
