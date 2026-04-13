from paper_garden.download import build_pdf_url, canonical_arxiv_id, slugify_title


def test_canonical_arxiv_id_accepts_abs_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/abs/2501.01234") == "2501.01234"


def test_canonical_arxiv_id_accepts_pdf_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/pdf/2501.01234.pdf") == "2501.01234"


def test_build_pdf_url_uses_canonical_id() -> None:
    assert build_pdf_url("2501.01234v2") == "https://arxiv.org/pdf/2501.01234v2.pdf"


def test_slugify_title_is_filesystem_safe() -> None:
    assert slugify_title("A/B Testing: Paper Garden?") == "a_b_testing_paper_garden"
