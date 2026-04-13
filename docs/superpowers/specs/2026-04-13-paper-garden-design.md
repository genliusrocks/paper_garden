# Paper Garden Design

## Goal

Publish `paper-garden` as a public, skills-first project for Codex users.

The first release should let a user install one skill and then run a single-paper ingest workflow that:

- accepts one arXiv `abs` URL, `pdf` URL, `html` URL, or paper id
- downloads the paper PDF
- converts the PDF to Markdown with `marker`
- generates a wiki note
- updates the garden index
- updates tag index files

This release does not include bulk review workflows across multiple papers. That is a later phase.

## Product Shape

`paper-garden` is a Codex skill, not a general-purpose CLI product.

The repository should still contain normal Python implementation code, but the public entrypoint is the skill itself. Users install the skill once and can then use it from any session.

The project should be fully self-contained except for dependencies installed through `uv`.

## User Configuration

The skill owns its own configuration.

Configuration file location:

- `skills/paper-garden/paper_garden.toml`

Initial configuration:

```toml
garden_dir = "./paper_garden"
language = "en"
```

Rules:

- `garden_dir` is the default output location for the user's knowledge garden
- `language` controls generated content language
- the installation flow must require the user to set these two values, while still providing the defaults above
- the skill reads this config on every run

## Main Workflow

The public workflow is one-shot single-paper ingest.

Input:

- one arXiv identifier or URL

Behavior:

1. Resolve the input into one canonical arXiv paper id
2. Create `garden_dir` if it does not exist
3. Initialize garden structure if needed
4. Download the PDF into the paper's storage directory
5. Convert the PDF to Markdown using `marker`
6. Generate a wiki note in the configured language
7. Suggest or assign tags
8. Update `index.md`
9. Update `tags/*.md`

Output:

- one fully ingested paper directory
- one updated global index
- one or more updated tag files

## Garden Structure

All generated knowledge base content lives under `garden_dir`.

Expected structure:

```text
<garden_dir>/
  index.md
  papers/
    <paper_slug>/
      paper.pdf
      extracted/
        paper.md
        paper.json
      wiki.md
      metadata.toml
  tags/
    <tag_name>.md
```

Notes:

- `paper_slug` should be stable and filesystem-safe
- `metadata.toml` should retain durable paper metadata such as title, arXiv id, source URL, language, and chosen tags
- repository source code should not mix with generated garden content

## Repository Structure

Recommended repository structure:

```text
paper-garden/
  README.md
  pyproject.toml
  skills/
    paper-garden/
      SKILL.md
      paper_garden.toml
      scripts/
        run.py
  src/
    paper_garden/
      config.py
      init.py
      download.py
      extract.py
      wiki.py
      tags.py
      index.py
      ingest.py
  templates/
    wiki.md
    index.md
    tag.md
  docs/
    superpowers/
      specs/
        2026-04-13-paper-garden-design.md
```

Design intent:

- `skills/` contains Codex-facing entrypoints and skill-owned config
- `src/paper_garden/` contains reusable implementation code
- `templates/` contains output templates, not executable logic

## Component Design

### `config.py`

Responsibilities:

- load `paper_garden.toml`
- validate required fields
- resolve `garden_dir` into an absolute path at runtime

### `init.py`

Responsibilities:

- create `garden_dir`
- create `papers/`, `tags/`, and `index.md` if missing
- keep initialization idempotent

### `download.py`

Responsibilities:

- normalize arXiv ids and supported URLs
- fetch metadata needed for naming and indexing
- download the PDF into the target paper directory

### `extract.py`

Responsibilities:

- invoke `marker`
- write extracted outputs into `extracted/`
- return stable paths to the main Markdown and JSON artifacts

### `wiki.py`

Responsibilities:

- read extracted content
- generate a concise reusable wiki note
- honor `language`
- avoid verbose narrative output

### `tags.py`

Responsibilities:

- assign tags for the paper
- create missing tag index files
- append or update entries idempotently

### `index.py`

Responsibilities:

- update `index.md`
- keep one stable entry per paper
- include paper title, local path, and tags

### `ingest.py`

Responsibilities:

- orchestrate the full one-shot workflow
- expose one main function for the skill wrapper

## Tagging and Index Rules

First release should optimize for simplicity and determinism.

Rules:

- one paper must have exactly one global index entry
- each tag file contains a flat list of linked papers with short summaries
- rerunning ingest for the same paper should update existing entries instead of duplicating them
- if automatic tagging quality is weak, keep the tag schema small and conservative in v1

## Dependency Policy

External dependencies should be easy for users to install.

Allowed dependency types:

- Python packages managed in `pyproject.toml`
- `uv` for environment and command execution
- `marker` as the PDF extraction backend

Not allowed:

- machine-specific absolute paths
- hidden local helper scripts outside this repository
- runtime dependencies that only exist in the author's personal workspace

## README Requirements

The public README should cover:

- what the skill does
- who it is for
- required prerequisites
- how to install dependencies with `uv`
- how to install or register the skill
- how to set `garden_dir` and `language`
- one complete ingest example
- expected output directory structure
- known limitations in v1

README should avoid describing future bulk review capabilities as if they already exist.

## Error Handling

The workflow should fail clearly when:

- config file is missing or invalid
- arXiv input cannot be resolved
- PDF download fails
- `marker` conversion fails
- generated garden files cannot be written

Errors should be actionable and reference the failed stage.

## Testing Strategy

First release should include lightweight verification around stable pieces:

- config loading
- arXiv input normalization
- slug generation
- idempotent garden initialization
- idempotent index updates
- idempotent tag updates

The `marker` execution path can be covered with a thinner integration test or smoke test due to heavier external dependencies.

## Out of Scope

Not included in the first public release:

- multi-paper literature review flow
- search-result batch download
- interactive UI
- database-backed storage
- advanced de-duplication across non-arXiv sources

## Open Implementation Decisions Already Resolved

These points were clarified during brainstorming:

- public product shape: Codex skill
- primary release workflow: one-shot ingest for a single paper
- internal implementation style: modular
- configuration ownership: skill-level config
- default config values:
  - `garden_dir = "./paper_garden"`
  - `language = "en"`
- project language: repository content in English, discussion with the author may remain in Chinese

## Implementation Readiness

This scope is small enough for one implementation plan.

The critical path is:

1. scaffold repo structure and dependency metadata
2. implement config and init
3. implement arXiv download and extraction
4. implement wiki and tag/index update logic
5. wire the skill wrapper
6. write README and smoke-test the full ingest path
