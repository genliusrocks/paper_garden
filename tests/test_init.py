from pathlib import Path

from paper_garden.init import ensure_garden


def test_ensure_garden_creates_required_structure(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir)

    assert (garden_dir / "papers").is_dir()
    assert (garden_dir / "tags").is_dir()
    assert (garden_dir / "index.md").is_file()
    assert (garden_dir / "AGENTS.md").is_file()
    assert (garden_dir / ".claude" / "CLAUDE.md").is_file()


def test_ensure_garden_is_idempotent(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir)
    ensure_garden(garden_dir)

    assert (garden_dir / "index.md").read_text(encoding="utf-8").startswith("# Paper Garden")


def test_ensure_garden_uses_chinese_guide(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir, language="中文")

    text = (garden_dir / "AGENTS.md").read_text(encoding="utf-8")
    assert "三层内容结构" in text


def test_ensure_garden_uses_english_guide_by_default(tmp_path: Path) -> None:
    garden_dir = tmp_path / "paper_garden"

    ensure_garden(garden_dir, language="en")

    text = (garden_dir / "AGENTS.md").read_text(encoding="utf-8")
    assert "Three-Tier Content Structure" in text
