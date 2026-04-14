from pathlib import Path

import tomli_w

from paper_garden.locate import LocatedPaper, locate


def _make_garden(tmp_path: Path) -> Path:
    garden = tmp_path / "garden"
    (garden / "papers" / "2408.03594_sample").mkdir(parents=True)
    (garden / "tags").mkdir()
    (garden / "index.md").write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- `pg-2024-00001` [Sample Paper](papers/2408.03594_sample/wiki.md) | tags: a, b — one-line summary\n",
        encoding="utf-8",
    )
    (garden / "papers" / "2408.03594_sample" / "metadata.toml").write_text(
        tomli_w.dumps({
            "id": "pg-2024-00001",
            "year": "2024",
            "title": "Sample Paper",
            "source_ref": "https://arxiv.org/abs/2408.03594",
            "source_kind": "arxiv",
            "language": "en",
            "tags": ["a", "b"],
            "arxiv_id": "2408.03594",
        }),
        encoding="utf-8",
    )
    return garden


def test_locate_finds_paper_via_index(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    result = locate(garden, "pg-2024-00001")
    assert isinstance(result, LocatedPaper)
    assert result.paper_id == "pg-2024-00001"
    assert result.paper_dir == garden / "papers" / "2408.03594_sample"
    assert result.wiki_path == garden / "papers" / "2408.03594_sample" / "wiki.md"
    assert result.extracted_markdown == garden / "papers" / "2408.03594_sample" / "extracted" / "document.md"
    assert result.title == "Sample Paper"
    assert result.tags == ["a", "b"]
    assert result.year == "2024"


def test_locate_returns_none_when_not_found(tmp_path: Path) -> None:
    garden = _make_garden(tmp_path)
    assert locate(garden, "pg-2024-99999") is None
