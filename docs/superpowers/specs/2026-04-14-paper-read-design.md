# Paper Read Skill/Command Design

**Date:** 2026-04-14
**Status:** Approved, pending implementation plan

## Purpose

Let an agent (Claude Code or Codex) read a paper from the garden by its `pg-YYYY-xxxxx` ID in any session, answer questions against it, and optionally update the wiki when it finds errors or gaps. Pairs with the existing `paper-garden` ingest skill/command.

## Scope

One new skill (`paper-read`) + matching Claude Code command. Shares configuration and Python package with `paper-garden`. No MCP server, no cross-garden support, no fuzzy ID matching.

## Trigger

Explicit invocation only:
- Claude Code: `/paper-read pg-2024-00005 <question>`
- Codex: skill invoked with `$ARGUMENTS = "pg-2024-00005 <question>"`

The agent does NOT auto-trigger on seeing an ID in chat.

## Components

### 1. `src/paper_garden/locate.py` (new)

Single responsibility: turn a paper ID into filesystem paths.

```python
@dataclass(frozen=True)
class LocatedPaper:
    paper_id: str
    paper_dir: Path
    wiki_path: Path
    extracted_markdown: Path  # may not exist; agent handles
    title: str
    tags: list[str]
    year: str


def locate(garden_dir: Path, paper_id: str) -> LocatedPaper | None:
    ...
```

**Strategy C** — two-step lookup:
1. Scan `garden_dir/index.md` line-by-line with `ids.ID_RE`. On match, derive `paper_dir` from the wiki link (`papers/<slug>/wiki.md`), then open `paper_dir/metadata.toml` to fill title/tags/year.
2. If index.md has no matching line, fallback: glob `garden_dir/papers/*/metadata.toml`, parse each, return the one whose `id` field matches.
3. If neither finds a match, return `None`.

### 2. `skills/paper-read/scripts/locate.py` (new)

Thin CLI over `paper_garden.locate`. Signature:

```bash
uv run python skills/paper-read/scripts/locate.py pg-2024-00005 --config skills/paper-garden/paper_garden.toml
```

- On success: print JSON `{paper_id, paper_dir, wiki_path, extracted_markdown, title, tags, year, garden_dir, language}` to stdout, exit 0.
- On miss: write `paper id 'pg-2024-00005' not found` to stderr, exit 1.

Reuses `paper_garden.config.load_config`. The config path defaults to the shared `skills/paper-garden/paper_garden.toml` so both skills use the same garden.

### 3. `skills/paper-read/SKILL.md` (new)

Codex skill entry. Documents the agent workflow:

**Step 1: Locate.** Run the locate script with the ID. If it fails, report "paper id not found, check spelling" and stop.

**Step 2: Read wiki.** Read `wiki_path`. This is mandatory and cheap.

**Step 3: Answer or escalate.**
- If the wiki is sufficient for the user's question, answer directly citing the wiki.
- If not, read `extracted_markdown`. For long papers, use `grep`/section anchors to find relevant content rather than reading the whole file. Answer once you have enough context.
- If `extracted_markdown` is missing, tell the user the paper was ingested without extraction and offer to re-run ingest.

**Step 4: Optional wiki update.** While reading the full text, if the agent notices a wiki error or a meaningful gap relevant to the user's question:
- Propose a patch: show the original snippet and the proposed replacement side by side.
- Wait for user confirmation (approve / edit / skip).
- On approval, apply via the `Edit` tool with exact string replacement. Do NOT rewrite the whole wiki. Do NOT auto-apply.

**Step 5: Report.** Summarize what was read (wiki only vs. wiki + full text sections X/Y) and any wiki updates applied.

### 4. `commands/paper-read.md` (new)

Claude Code mirror of the skill. Uses `__PAPER_GARDEN_REPO__` placeholder replaced at install. `$ARGUMENTS` is the full string; the agent splits on first whitespace to separate `paper_id` from the question.

### 5. README + install

Add a second install line:

```bash
cp commands/paper-read.md ~/.claude/commands/paper-read.md
sed -i "s|__PAPER_GARDEN_REPO__|$(pwd)|g" ~/.claude/commands/paper-read.md
```

## Data Flow

```
/paper-read pg-2024-00005 <question>
  ↓
locate.py → JSON {paper_dir, wiki_path, extracted_markdown, title, tags, year, ...}
  ↓
agent reads wiki.md (always)
  ↓
sufficient? ─yes→ answer
         └─no→ read extracted/document.md (targeted: grep, sections)
                 ↓
               answer
                 ↓
            found wiki error/gap?
              └─yes→ propose patch → user confirm → Edit
```

## Error Handling

- **ID not found:** locate script exits 1 with stderr message. Agent reports to user: "paper id '<id>' not found — check spelling or that ingest completed."
- **Garden not configured:** `load_config` raises `ConfigurationRequiredError`; agent tells user to run configure.py.
- **wiki.md missing:** rare (old paper, failed ingest). Agent reads `extracted_markdown` instead and tells the user the wiki is missing.
- **extracted_markdown missing:** agent answers from wiki only and flags that deeper questions require re-running extract.
- **metadata.toml missing `id`:** treated as not-yet-migrated. locate skips in fallback; user should run migrate_ids.

## Testing

### New: `tests/test_locate.py`

- `test_locate_finds_paper_via_index` — standard case
- `test_locate_falls_back_to_metadata_when_index_missing_id` — simulate index drift
- `test_locate_returns_none_when_not_found`
- `test_locate_reads_metadata_fields_correctly` — title/tags/year populated
- `test_locate_handles_missing_wiki_and_extracted_paths` — paths returned even if not on disk; existence checks are the agent's job

### Updated: `tests/test_skill_bundle.py`

- `test_paper_read_scripts_import_from_package` — `skills/paper-read/scripts/locate.py` imports `paper_garden.locate`
- `test_paper_read_skill_md_references_locate_script` — SKILL.md mentions the script path and the `$ARGUMENTS` contract

## Non-Goals

- Cross-garden lookup (each install points at one `garden_dir`).
- Fuzzy ID matching / typo correction.
- Auto-apply wiki updates without user confirmation.
- Bulk wiki rewriting; updates are per-Edit.
- MCP server exposure (separate effort if ever needed).
- Auto-triggering on ID mentions in chat — invocation is explicit only.

## Out of Scope

- Changes to `paper-garden` ingest flow.
- Changes to `ids` module, `index.py`, or `tags.py`.
- Multi-paper comparison in one call (agent can call `/paper-read` multiple times).
