from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


def test_skill_scripts_do_not_depend_on_repo_src_path() -> None:
    run_script = Path("skills/paper-garden/scripts/run.py").read_text(encoding="utf-8")
    configure_script = Path("skills/paper-garden/scripts/configure.py").read_text(encoding="utf-8")

    assert ' / "src"' not in run_script
    assert "parents[3]" not in run_script
    assert ' / "src"' not in configure_script
    assert "parents[3]" not in configure_script


def test_installed_skill_scripts_run_from_copied_skill_dir(tmp_path: Path) -> None:
    source_skill_dir = Path("skills/paper-garden").resolve()
    installed_skill_dir = tmp_path / "paper-garden"
    shutil.copytree(source_skill_dir, installed_skill_dir)

    run_result = subprocess.run(
        [sys.executable, str(installed_skill_dir / "scripts" / "run.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    configure_result = subprocess.run(
        [sys.executable, str(installed_skill_dir / "scripts" / "configure.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert run_result.returncode == 0, run_result.stderr
    assert "input_value" in run_result.stdout
    assert configure_result.returncode == 0, configure_result.stderr
    assert "--garden-dir" in configure_result.stdout
