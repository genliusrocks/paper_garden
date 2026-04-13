from pathlib import Path

from paper_garden.tags import update_tag_files


def test_update_tag_files_creates_one_file_per_tag(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag", "agents"])

    assert (tags_dir / "rag.md").is_file()
    assert (tags_dir / "agents.md").is_file()
