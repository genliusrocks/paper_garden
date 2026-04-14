import sys
from pathlib import Path

import tomli_w


def _setup_garden(tmp_path: Path) -> Path:
    garden = tmp_path / "garden"
    (garden / "papers" / "2408.03594_sample").mkdir(parents=True)
    (garden / "papers" / "local_paper").mkdir(parents=True)
    (garden / "tags").mkdir()

    (garden / "index.md").write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- (2024) [Sample ArXiv](papers/2408.03594_sample/wiki.md) | tags: t1 — summary A\n"
        "- [Local Paper](papers/local_paper/wiki.md) | tags: t1, t2 — summary B\n",
        encoding="utf-8",
    )

    (garden / "tags" / "t1.md").write_text(
        "# t1\n\n"
        "- (2024) [Sample ArXiv](papers/2408.03594_sample/wiki.md) — summary A\n"
        "- [Local Paper](papers/local_paper/wiki.md) — summary B\n",
        encoding="utf-8",
    )
    (garden / "tags" / "t2.md").write_text(
        "# t2\n\n"
        "- [Local Paper](papers/local_paper/wiki.md) — summary B\n",
        encoding="utf-8",
    )

    (garden / "papers" / "2408.03594_sample" / "metadata.toml").write_text(
        tomli_w.dumps({
            "title": "Sample ArXiv",
            "arxiv_id": "2408.03594",
            "source_ref": "https://arxiv.org/abs/2408.03594",
            "source_kind": "arxiv",
            "language": "en",
            "tags": ["t1"],
        }),
        encoding="utf-8",
    )
    (garden / "papers" / "local_paper" / "metadata.toml").write_text(
        tomli_w.dumps({
            "title": "Local Paper",
            "source_ref": "/tmp/local.pdf",
            "source_kind": "local",
            "language": "en",
            "tags": ["t1", "t2"],
        }),
        encoding="utf-8",
    )
    return garden


def _import_migrate():
    scripts_dir = Path(__file__).resolve().parents[1] / "skills" / "paper-garden" / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    if "migrate_ids" in sys.modules:
        del sys.modules["migrate_ids"]
    import migrate_ids
    return migrate_ids


def test_migration_assigns_sequential_ids(tmp_path: Path, monkeypatch) -> None:
    garden = _setup_garden(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2023")

    migrate_ids = _import_migrate()
    migrate_ids.run_migration(garden)

    index_content = (garden / "index.md").read_text(encoding="utf-8")
    assert "`pg-2024-00001` [Sample ArXiv]" in index_content
    assert "`pg-2023-00002` [Local Paper]" in index_content
    assert "(2024)" not in index_content


def test_migration_writes_id_to_metadata(tmp_path: Path, monkeypatch) -> None:
    garden = _setup_garden(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2023")

    migrate_ids = _import_migrate()
    migrate_ids.run_migration(garden)

    arxiv_meta = (garden / "papers" / "2408.03594_sample" / "metadata.toml").read_text(encoding="utf-8")
    assert 'id = "pg-2024-00001"' in arxiv_meta
    assert 'year = "2024"' in arxiv_meta

    local_meta = (garden / "papers" / "local_paper" / "metadata.toml").read_text(encoding="utf-8")
    assert 'id = "pg-2023-00002"' in local_meta
    assert 'year = "2023"' in local_meta


def test_migration_updates_tag_files(tmp_path: Path, monkeypatch) -> None:
    garden = _setup_garden(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2023")

    migrate_ids = _import_migrate()
    migrate_ids.run_migration(garden)

    t1 = (garden / "tags" / "t1.md").read_text(encoding="utf-8")
    assert "`pg-2024-00001` [Sample ArXiv]" in t1
    assert "`pg-2023-00002` [Local Paper]" in t1
    assert "(2024)" not in t1

    t2 = (garden / "tags" / "t2.md").read_text(encoding="utf-8")
    assert "`pg-2023-00002` [Local Paper]" in t2


def test_migration_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    garden = _setup_garden(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2023")

    migrate_ids = _import_migrate()
    migrate_ids.run_migration(garden)
    index_after_first = (garden / "index.md").read_text(encoding="utf-8")

    migrate_ids.run_migration(garden)
    index_after_second = (garden / "index.md").read_text(encoding="utf-8")

    assert index_after_first == index_after_second
