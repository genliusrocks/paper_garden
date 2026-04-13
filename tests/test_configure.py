from pathlib import Path

from paper_garden.configure import write_config
from paper_garden.config import load_config


def test_write_config_uses_defaults(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "paper_garden.toml"
    monkeypatch.chdir(tmp_path)

    write_config(config_path, garden_dir=None, language=None)
    config = load_config(config_path)

    assert config.garden_dir == tmp_path / "paper_garden"
    assert config.language == "en"


def test_write_config_accepts_explicit_values(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "paper_garden.toml"
    monkeypatch.chdir(tmp_path)

    write_config(config_path, garden_dir="./notes", language="zh")
    config = load_config(config_path)

    assert config.garden_dir == tmp_path / "notes"
    assert config.language == "zh"
