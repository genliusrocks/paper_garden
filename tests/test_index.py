from pathlib import Path

from paper_garden.index import update_index


def test_update_index_adds_single_entry(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")

    update_index(
        index_path,
        paper_id="pg-2024-00001",
        title="Attention Is All You Need",
        paper_rel_dir="papers/attention",
        tags=["transformer"],
        summary=None,
    )

    content = index_path.read_text(encoding="utf-8")
    assert "- `pg-2024-00001` [Attention Is All You Need](papers/attention/wiki.md) | tags: transformer" in content


def test_update_index_includes_summary(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")

    update_index(
        index_path,
        paper_id="pg-2024-00001",
        title="Paper",
        paper_rel_dir="papers/p",
        tags=["t1"],
        summary="one-line summary",
    )

    content = index_path.read_text(encoding="utf-8")
    assert "- `pg-2024-00001` [Paper](papers/p/wiki.md) | tags: t1 — one-line summary" in content


def test_update_index_dedups_by_paper_id(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- `pg-2024-00001` [Old Title](papers/p/wiki.md) | tags: old — old summary\n",
        encoding="utf-8",
    )

    update_index(
        index_path,
        paper_id="pg-2024-00001",
        title="New Title",
        paper_rel_dir="papers/p",
        tags=["new"],
        summary="new summary",
    )

    content = index_path.read_text(encoding="utf-8")
    assert "Old Title" not in content
    assert content.count("pg-2024-00001") == 1
    assert "New Title" in content


def test_update_index_preserves_existing_summary_when_not_provided(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- `pg-2024-00001` [Title](papers/p/wiki.md) | tags: t1 — original summary\n",
        encoding="utf-8",
    )

    update_index(
        index_path,
        paper_id="pg-2024-00001",
        title="Title",
        paper_rel_dir="papers/p",
        tags=["t1", "t2"],
        summary=None,
    )

    content = index_path.read_text(encoding="utf-8")
    assert "— original summary" in content
    assert "tags: t1, t2" in content
