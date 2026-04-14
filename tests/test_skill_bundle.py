from __future__ import annotations

from pathlib import Path


def test_skill_scripts_import_from_package() -> None:
    """Skill scripts should import from the paper_garden package, not duplicate code."""
    scripts_dir = Path("skills/paper-garden/scripts")
    for script in scripts_dir.glob("*.py"):
        text = script.read_text(encoding="utf-8")
        assert "from paper_garden" in text or script.name == "__init__.py", (
            f"{script.name} does not import from paper_garden package"
        )


def test_no_duplicate_runtime_scripts() -> None:
    """Ensure _runtime.py and _configure.py duplicates are gone."""
    scripts_dir = Path("skills/paper-garden/scripts")
    assert not (scripts_dir / "_runtime.py").exists()
    assert not (scripts_dir / "_configure.py").exists()


def test_skill_md_references_two_step_workflow() -> None:
    """SKILL.md should reference download.py and finalize.py for the two-step workflow."""
    skill_md = Path("skills/paper-garden/SKILL.md").read_text(encoding="utf-8")
    assert "download.py" in skill_md
    assert "finalize.py" in skill_md
    assert "First-Time Setup" in skill_md
