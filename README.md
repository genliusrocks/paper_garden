# Paper Garden

[![CI](https://github.com/genliusrocks/paper_garden/actions/workflows/ci.yml/badge.svg)](https://github.com/genliusrocks/paper_garden/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

Turn academic papers into a searchable Markdown knowledge garden with Claude Code or Codex.

Paper Garden is an agent-friendly workflow for ingesting arXiv papers and local PDFs into a plain-text research repository. Give your coding agent a paper link or file, and it downloads the source, extracts the text, drafts a structured wiki, suggests tags, and updates a browsable index after your review.

It is built for people who want research notes to stay in git, stay readable, and stay useful to both humans and LLM agents.

## Why Paper Garden

Reading papers is slow. Organizing them is slower. Paper Garden offloads the repetitive work, so you spend time understanding papers instead of filing them.

The output is plain Markdown in a normal git repository. No proprietary database, no hosted app, no lock-in. Your garden works with any editor, any search tool, and any LLM that can read files.

- Plain Markdown instead of a proprietary database
- Git-friendly structure that works in your existing note repo
- Human review before tags and index summaries are written
- Agent-readable layout for Claude Code, Codex, and similar tools
- Re-runnable ingestion workflow without turning your notes into a black box

## Use Cases

- Build a personal paper-reading garden that stays searchable in git
- Maintain a shared lab or team repository of paper summaries
- Preprocess papers into structured notes for downstream agent research
- Keep extracted source text next to higher-level wiki notes for traceability

## How It Works

```text
You: "ingest https://arxiv.org/abs/1706.03762"

Agent:  1. Downloads the PDF and extracts full text via marker
        2. Generates a structured wiki (summary, method, results, limitations, terms)
        3. Suggests tags: transformer, attention, sequence-modeling
        4. Proposes a one-line summary for the index

You:    Review the tags and summary, then confirm or adjust them

Agent:  5. Writes wiki.md, updates index.md and tag files
        6. Done - the paper is in your garden
```

Duplicate papers are detected before finalizing, so retrying an already-indexed paper is treated as a no-op instead of rewriting your garden.

## Example Output

`index.md`

```md
# Paper Garden

## Papers

- (2017) [Attention Is All You Need](papers/1706.03762_attention_is_all_you_need/wiki.md) | tags: transformer, attention, sequence-modeling — Introduces the Transformer architecture for sequence modeling without recurrence.
```

`papers/1706.03762_attention_is_all_you_need/wiki.md`

```md
# Attention Is All You Need

## Summary
The paper replaces recurrent sequence modeling with stacked self-attention and feed-forward layers, improving parallelism and translation quality.

## Method
- Encoder-decoder Transformer with multi-head self-attention
- Positional encodings instead of recurrence
- Fully parallel training across tokens

## Results
- State-of-the-art BLEU on WMT 2014 En-De and En-Fr
- Lower training cost than comparable recurrent models
```

## Garden Structure

```text
your-garden/
├── index.md                          # Master index: all papers with year, tags, summary
├── tags/
│   ├── transformer.md                # Papers tagged "transformer"
│   └── attention.md
├── papers/
│   └── 1706.03762_attention_is_all_you_need/
│       ├── wiki.md                   # LLM-generated structured analysis
│       ├── paper.pdf                 # Original PDF
│       ├── metadata.toml             # Source URL, arXiv ID, tags
│       └── extracted/
│           ├── document.md           # Full text extracted by marker
│           └── document.json
├── AGENTS.md                         # Three-tier content guide for agents
└── .claude/CLAUDE.md                 # Agent instructions for this garden
```

**Three content tiers:**
1. **Index & tags** - title, year, 100-character summary. Immutable after creation. Start here for browsing.
2. **Wiki** - structured analysis (summary, problem, method, results, limitations, terms). Updatable as understanding deepens.
3. **Extracted full text** - complete Markdown and JSON from marker. Reference this when the wiki is not enough.

## Design Principles

- **Markdown over databases**: every artifact is inspectable, searchable, and versionable.
- **Review before write**: the agent proposes tags and the index summary before finalizing.
- **Stable top-level navigation**: index and tag summaries are short, deliberate, and treated as fixed once written.
- **Layered paper storage**: index for discovery, wiki for understanding, extraction for raw detail.
- **Agent-operable layout**: the repository structure is meant to be legible to both people and coding agents.

## Supported Inputs

- arXiv URLs (`abs`, `html`, `pdf`)
- arXiv paper IDs (for example `1706.03762`)
- Local PDF files

## Install

Clone the repo and sync dependencies:

```bash
git clone https://github.com/genliusrocks/paper_garden.git
cd paper_garden
uv sync --extra dev
```

### Claude Code

The skill is auto-discovered when you work from the repo directory. On first use, Claude will ask you to configure your garden directory and wiki language.

### Codex

Point Codex at the `skills/paper-garden/` directory. The `SKILL.md` file contains the end-to-end workflow instructions.

### Local CLI / development use

You can also run the helper scripts directly:

```bash
uv run python skills/paper-garden/scripts/configure.py --garden-dir "~/my-garden" --language "en"
uv run python skills/paper-garden/scripts/download.py "https://arxiv.org/abs/1706.03762" --config skills/paper-garden/paper_garden.toml
```

## Configuration

Configuration is created on first use. You can also set it manually:

```bash
uv run python skills/paper-garden/scripts/configure.py \
  --garden-dir "~/my-garden" \
  --language "en"
```

| Option | Default | Description |
|--------|---------|-------------|
| `garden_dir` | `./paper_garden` | Where the garden lives. Can be a separate git repo. |
| `language` | `en` | Language for generated wiki content (for example `en` or `zh`). |

## Non-goals

- Not a reference manager or BibTeX replacement
- Not a hosted web app or collaborative SaaS
- Not a PDF annotation tool
- Not a general-purpose note-taking framework outside paper ingestion

## Development

```bash
uv sync --extra dev
uv run python -m pytest tests/ -v
```

## Contributing

Issues and pull requests are welcome. If you change ingest behavior, keep the user-facing workflow stable: configuration should remain explicit, duplicate checks should be non-destructive, and generated artifacts should stay plain Markdown.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [marker](https://github.com/VikParuchuri/marker) (invoked via `uvx` - no manual install needed)

## License

MIT
