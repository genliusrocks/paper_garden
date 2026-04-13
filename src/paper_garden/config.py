from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


class ConfigurationRequiredError(ValueError):
    pass


@dataclass(frozen=True)
class PaperGardenConfig:
    garden_dir: Path
    language: str


def load_config(config_path: Path) -> PaperGardenConfig:
    if not config_path.is_file():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    garden_dir = data.get("garden_dir")
    language = data.get("language")

    if not isinstance(garden_dir, str) or not garden_dir.strip():
        raise ConfigurationRequiredError(
            "Paper Garden is not configured. Run "
            "`uv run python skills/paper-garden/scripts/configure.py --garden-dir ... --language ...`."
        )
    if not isinstance(language, str) or not language.strip():
        raise ConfigurationRequiredError(
            "Paper Garden is not configured. Run "
            "`uv run python skills/paper-garden/scripts/configure.py --garden-dir ... --language ...`."
        )

    garden_dir_path = Path(garden_dir).expanduser()
    if not garden_dir_path.is_absolute():
        garden_dir_path = (Path.cwd() / garden_dir_path).resolve()

    return PaperGardenConfig(
        garden_dir=garden_dir_path,
        language=language.strip(),
    )
