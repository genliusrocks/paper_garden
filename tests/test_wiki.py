from paper_garden.wiki import build_wiki


def test_build_wiki_returns_template_with_title() -> None:
    wiki = build_wiki("Test Title", "Extracted text", "en")
    assert "# Test Title" in wiki
    assert "## Summary" in wiki
    assert "## Method" in wiki
