from __future__ import annotations

from pathlib import Path


DEFAULT_INDEX = "# Paper Garden\n\n## Papers\n\n"


def _garden_guide(language: str) -> str:
    if language.lower().startswith("zh") or language == "中文":
        return """\
# Paper Garden 知识库

## 三层内容结构

本知识库的论文内容按三层组织：

### 第一层：索引与标签（index.md / tags/*.md）
存储论文名称、发表年份和不超过100字的核心概要。
此层内容一旦生成即为定稿，不再修改。浏览和检索论文时从这里开始。

### 第二层：Wiki 笔记（papers/<slug>/wiki.md）
论文的结构化分析，包括摘要、问题、方法、结果、局限和术语。
这是日常搜索论文内容的主要目的地。此层内容可能随理解深入而持续更新。

### 第三层：全文提取（papers/<slug>/extracted/）
由 marker 从 PDF 提取的完整 Markdown 和 JSON。
当 Wiki 笔记信息不足时，到这里查阅原文细节。

## 使用指南
- 查找论文：先看 index.md 或 tags/ 目录
- 了解论文：读对应的 wiki.md
- 查原文细节：读 extracted/ 下的完整提取内容
"""
    return """\
# Paper Garden Knowledge Base

## Three-Tier Content Structure

Paper content in this garden is organized in three tiers:

### Tier 1: Index & Tags (index.md / tags/*.md)
Paper title, publication year, and a summary of up to 100 characters.
This tier is immutable once generated. Start browsing and searching here.

### Tier 2: Wiki Notes (papers/<slug>/wiki.md)
Structured analysis: summary, problem, method, results, limitations, terms.
This is the primary destination when searching for paper content. May be updated over time.

### Tier 3: Full Extraction (papers/<slug>/extracted/)
Complete Markdown and JSON extracted from the PDF by marker.
Consult this when wiki notes lack sufficient detail.

## Usage Guide
- Find papers: check index.md or the tags/ directory
- Understand a paper: read its wiki.md
- Full text details: read extracted/ content
"""


def ensure_garden(garden_dir: Path, language: str = "en") -> None:
    garden_dir.mkdir(parents=True, exist_ok=True)
    (garden_dir / "papers").mkdir(exist_ok=True)
    (garden_dir / "tags").mkdir(exist_ok=True)

    index_path = garden_dir / "index.md"
    if not index_path.exists():
        index_path.write_text(DEFAULT_INDEX, encoding="utf-8")

    guide = _garden_guide(language)

    agents_path = garden_dir / "AGENTS.md"
    if not agents_path.exists():
        agents_path.write_text(guide, encoding="utf-8")

    claude_dir = garden_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    claude_md_path = claude_dir / "CLAUDE.md"
    if not claude_md_path.exists():
        claude_md_path.write_text(guide, encoding="utf-8")
