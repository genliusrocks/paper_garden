# Paper Garden

[![CI](https://github.com/genliusrocks/paper_garden/actions/workflows/ci.yml/badge.svg)](https://github.com/genliusrocks/paper_garden/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

A Claude Code command and Codex skill that turns academic papers into a searchable Markdown knowledge garden.

Give your coding agent a paper link or local PDF. It downloads the source, extracts full text, drafts a structured wiki, suggests tags, and updates a browsable index — all after your review. The output is plain Markdown in a git repo, readable by both humans and LLM agents.

## Why

- Plain Markdown in git — no database, no hosted app, no lock-in
- Human reviews tags and summary before anything is written
- Agent-readable layout that works as context for follow-up research
- Duplicate detection prevents re-ingesting the same paper

## How It Works

```text
You:    /paper-garden https://arxiv.org/abs/1706.03762

Agent:  1. Downloads PDF, extracts full text via marker
        2. Generates structured wiki (summary, method, results, limitations, terms)
        3. Suggests tags and a one-line index summary

You:    Review and confirm tags + summary

Agent:  4. Writes wiki.md, updates index.md and tag files
```

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

## Supported Inputs

- arXiv URLs (`abs`, `html`, `pdf`)
- arXiv paper IDs (for example `1706.03762`)
- Local PDF files

## Install

```bash
git clone https://github.com/genliusrocks/paper_garden.git
cd paper_garden
uv sync
```

**Claude Code** — install as a global `/paper-garden` command:

```bash
cp commands/paper-garden.md ~/.claude/commands/paper-garden.md
sed -i "s|__PAPER_GARDEN_REPO__|$(pwd)|g" ~/.claude/commands/paper-garden.md
```

**Codex** — register the `skills/paper-garden/` directory as a skill.

On first use, the agent will ask you to configure your garden directory and wiki language.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `garden_dir` | `./paper_garden` | Where the garden lives. Can be a separate git repo. |
| `language` | `en` | Language for generated wiki content (for example `en` or `zh`). |

## Development

```bash
uv sync --extra dev
uv run python -m pytest tests/ -v
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [marker](https://github.com/VikParuchuri/marker) (invoked via `uvx` - no manual install needed)

## License

MIT
