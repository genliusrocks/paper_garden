from pathlib import Path

from paper_garden.index import update_index


def test_update_index_adds_single_entry(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")

    update_index(index_path, "Paper Title", "papers/paper-slug", ["rag", "agents"])

    text = index_path.read_text(encoding="utf-8")
    assert "- [Paper Title](papers/paper-slug/wiki.md) | tags: rag, agents" in text
