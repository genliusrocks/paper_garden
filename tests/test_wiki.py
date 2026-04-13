from paper_garden.wiki import build_wiki


def test_build_wiki_keeps_stable_headings_regardless_of_language() -> None:
    wiki = build_wiki("Test Title", "Extracted text", "zh")

    assert "# Test Title" in wiki
    assert "## Summary" in wiki
    assert "## Method" in wiki
