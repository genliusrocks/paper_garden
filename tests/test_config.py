from pathlib import Path

from paper_garden.config import load_config


def test_load_config_reads_skill_local_file(tmp_path: Path) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\nlanguage = "en"\n', encoding="utf-8")

    original_cwd = Path.cwd()
    config = load_config(config_path)

    assert config.garden_dir == original_cwd / "garden"
    assert config.language == "en"


def test_load_config_rejects_missing_language(tmp_path: Path) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\n', encoding="utf-8")

    try:
        load_config(config_path)
    except ValueError as exc:
        assert "language" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
