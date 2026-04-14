from pathlib import Path

from paper_garden.tags import update_tag_files


def test_update_tag_files_creates_one_file_per_tag(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag", "agents"])

    assert (tags_dir / "rag.md").is_file()
    assert (tags_dir / "agents.md").is_file()


def test_update_tag_files_includes_year(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag"], year="2017")

    text = (tags_dir / "rag.md").read_text(encoding="utf-8")
    assert "- (2017) [Paper Title](papers/paper-slug/wiki.md)" in text


def test_update_tag_files_includes_summary(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag"], year="2017", summary="A short summary")

    text = (tags_dir / "rag.md").read_text(encoding="utf-8")
    assert "- (2017) [Paper Title](papers/paper-slug/wiki.md) — A short summary" in text


def test_update_tag_files_preserves_summary_when_not_provided(tmp_path: Path) -> None:
    tags_dir = tmp_path / "tags"
    tags_dir.mkdir()

    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag"], year="2017", summary="Original summary")
    update_tag_files(tags_dir, "Paper Title", "papers/paper-slug", ["rag"], year="2017")

    text = (tags_dir / "rag.md").read_text(encoding="utf-8")
    assert "— Original summary" in text
