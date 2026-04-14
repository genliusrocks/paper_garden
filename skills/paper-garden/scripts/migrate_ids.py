#!/usr/bin/env python3
"""One-shot migration: assign pg-<year>-<hex5> IDs to existing papers."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

import tomli_w

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from paper_garden.download import year_from_arxiv_id
from paper_garden.ids import ID_RE, parse_existing_seqs


OLD_ENTRY_RE = re.compile(r"^-\s+(?:\((\d{4})\)\s+)?\[([^\]]+)\]\(([^)]+/wiki\.md)\)")


def _load_metadata(paper_dir: Path) -> dict:
    meta_path = paper_dir / "metadata.toml"
    if not meta_path.is_file():
        raise SystemExit(f"metadata.toml missing in {paper_dir}")
    return tomllib.loads(meta_path.read_text(encoding="utf-8"))


def _save_metadata(paper_dir: Path, data: dict) -> None:
    (paper_dir / "metadata.toml").write_text(tomli_w.dumps(data), encoding="utf-8")


def _ask_year_for(title: str) -> str:
    while True:
        answer = input(f"Publication year for '{title}' (YYYY): ").strip()
        if re.fullmatch(r"\d{4}", answer):
            return answer
        print("Please enter a 4-digit year.")


def _parse_old_index_entries(index_path: Path) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if ID_RE.match(line):
            continue
        m = OLD_ENTRY_RE.match(line)
        if m:
            entries.append((m.group(2), m.group(3), line))
    return entries


def _next_seq(index_path: Path) -> int:
    seqs = parse_existing_seqs(index_path)
    return (max(seqs) if seqs else 0) + 1


def _rewrite_line(old_line: str, paper_id: str) -> str:
    m = OLD_ENTRY_RE.match(old_line)
    if not m:
        return old_line
    tail = old_line[m.end():]
    return f"- `{paper_id}` [{m.group(2)}]({m.group(3)}){tail}"


def _rewrite_file(file_path: Path, wiki_link: str, paper_id: str) -> None:
    if not file_path.is_file():
        return
    lines = file_path.read_text(encoding="utf-8").splitlines()
    new_lines: list[str] = []
    for line in lines:
        m = OLD_ENTRY_RE.match(line)
        if m and m.group(3) == wiki_link and not ID_RE.match(line):
            new_lines.append(_rewrite_line(line, paper_id))
        else:
            new_lines.append(line)
    file_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")


def run_migration(garden_dir: Path) -> None:
    index_path = garden_dir / "index.md"
    tags_dir = garden_dir / "tags"

    entries = _parse_old_index_entries(index_path)
    for title, wiki_link, _old_line in entries:
        paper_rel = wiki_link.rsplit("/wiki.md", 1)[0]
        paper_dir = garden_dir / paper_rel

        meta = _load_metadata(paper_dir)
        if "id" in meta:
            continue

        arxiv_id = meta.get("arxiv_id")
        year = year_from_arxiv_id(arxiv_id) if arxiv_id else None
        if not year:
            year = _ask_year_for(title)

        seq = _next_seq(index_path)
        paper_id = f"pg-{year}-{seq:05x}"

        meta["id"] = paper_id
        meta["year"] = year
        _save_metadata(paper_dir, meta)

        _rewrite_file(index_path, wiki_link, paper_id)
        if tags_dir.is_dir():
            for tag_file in tags_dir.glob("*.md"):
                _rewrite_file(tag_file, wiki_link, paper_id)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assign paper IDs to an existing garden.")
    parser.add_argument("--config", required=True, help="Path to paper_garden.toml.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from paper_garden.config import load_config

    args = parse_args(argv)
    config = load_config(Path(args.config))
    run_migration(config.garden_dir)
    print("Migration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
