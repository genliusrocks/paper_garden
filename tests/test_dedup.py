from pathlib import Path

from paper_garden.dedup import check_duplicate, normalize_title


def test_normalize_title_basic() -> None:
    assert normalize_title("Attention Is All You Need") == "attention is all you need"


def test_normalize_title_preserves_punctuation() -> None:
    assert normalize_title("A/B Testing: Paper Garden?") == "a/b testing: paper garden?"


def test_normalize_title_collapses_whitespace() -> None:
    assert normalize_title("  Multi   Word   Title  ") == "multi word title"


def test_normalize_title_case_insensitive() -> None:
    assert normalize_title("attention is all you need") == normalize_title("Attention Is All You Need")


def test_normalize_title_underscore_filename() -> None:
    assert normalize_title("orderimbalance_trading") == normalize_title("OrderImbalance Trading")


def test_check_duplicate_finds_match(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- (2017) [Attention Is All You Need](papers/1706.03762_attention/wiki.md) | tags: transformer\n",
        encoding="utf-8",
    )

    result = check_duplicate(index_path, "attention is all you need")

    assert result.found is True
    assert "Attention Is All You Need" in result.existing_entry
    assert result.existing_paper_dir == "papers/1706.03762_attention"


def test_check_duplicate_no_match(tmp_path: Path) -> None:
    index_path = tmp_path / "index.md"
    index_path.write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- (2017) [Attention Is All You Need](papers/1706.03762_attention/wiki.md) | tags: transformer\n",
        encoding="utf-8",
    )

    result = check_duplicate(index_path, "BERT: Pre-training of Deep Bidirectional Transformers")

    assert result.found is False


def test_check_duplicate_missing_index(tmp_path: Path) -> None:
    result = check_duplicate(tmp_path / "nonexistent.md", "Any Title")

    assert result.found is False
