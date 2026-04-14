from pathlib import Path

from paper_garden.tags import update_tag_files


def test_update_tag_files_creates_one_file_per_tag(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(
        tags_dir,
        paper_id="pg-2024-00001",
        title="Paper",
        paper_rel_dir="papers/p",
        tags=["t1", "t2"],
        summary=None,
    )

    assert (tags_dir / "t1.md").is_file()
    assert (tags_dir / "t2.md").is_file()
    content = (tags_dir / "t1.md").read_text(encoding="utf-8")
    assert "- `pg-2024-00001` [Paper](papers/p/wiki.md)" in content


def test_update_tag_files_includes_summary(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(
        tags_dir,
        paper_id="pg-2024-00001",
        title="Paper",
        paper_rel_dir="papers/p",
        tags=["t1"],
        summary="one-line summary",
    )

    content = (tags_dir / "t1.md").read_text(encoding="utf-8")
    assert "- `pg-2024-00001` [Paper](papers/p/wiki.md) — one-line summary" in content


def test_update_tag_files_dedups_by_paper_id(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()
    (tags_dir / "t1.md").write_text(
        "# t1\n\n"
        "- `pg-2024-00001` [Old Title](papers/p/wiki.md) — old summary\n",
        encoding="utf-8",
    )

    update_tag_files(
        tags_dir,
        paper_id="pg-2024-00001",
        title="New Title",
        paper_rel_dir="papers/p",
        tags=["t1"],
        summary="new summary",
    )

    content = (tags_dir / "t1.md").read_text(encoding="utf-8")
    assert "Old Title" not in content
    assert content.count("pg-2024-00001") == 1
    assert "New Title" in content


def test_update_tag_files_preserves_summary_when_not_provided(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()
    (tags_dir / "t1.md").write_text(
        "# t1\n\n"
        "- `pg-2024-00001` [Title](papers/p/wiki.md) — original summary\n",
        encoding="utf-8",
    )

    update_tag_files(
        tags_dir,
        paper_id="pg-2024-00001",
        title="Title",
        paper_rel_dir="papers/p",
        tags=["t1"],
        summary=None,
    )

    content = (tags_dir / "t1.md").read_text(encoding="utf-8")
    assert "— original summary" in content
