from pathlib import Path

import requests

from paper_garden.download import build_pdf_url, canonical_arxiv_id, download_paper, slugify_title, year_from_arxiv_id


def test_canonical_arxiv_id_accepts_abs_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/abs/2501.01234") == "2501.01234"


def test_canonical_arxiv_id_accepts_pdf_url() -> None:
    assert canonical_arxiv_id("https://arxiv.org/pdf/2501.01234.pdf") == "2501.01234"


def test_build_pdf_url_uses_canonical_id() -> None:
    assert build_pdf_url("2501.01234v2") == "https://arxiv.org/pdf/2501.01234v2.pdf"


def test_slugify_title_is_filesystem_safe() -> None:
    assert slugify_title("A/B Testing: Paper Garden?") == "a_b_testing_paper_garden"


def test_download_paper_copies_local_pdf(tmp_path: Path) -> None:
    local_pdf = tmp_path / "My Paper.pdf"
    local_pdf.write_bytes(b"%PDF-1.4")
    papers_dir = tmp_path / "papers"

    result = download_paper(requests.Session(), str(local_pdf), papers_dir)

    assert result.source_kind == "local"
    assert result.source_ref == str(local_pdf.resolve())
    assert result.pdf_path.read_bytes() == b"%PDF-1.4"
    assert result.pdf_path.parent.name.endswith("my_paper")


def test_year_from_arxiv_id() -> None:
    assert year_from_arxiv_id("1706.03762") == "2017"
    assert year_from_arxiv_id("2501.01234") == "2025"
    assert year_from_arxiv_id(None) is None
    assert year_from_arxiv_id("hep-ph/9905221") is None


def test_resolved_paper_has_year_for_arxiv() -> None:
    from paper_garden.download import resolve_paper

    class FakeSession:
        def get(self, url, timeout):
            class R:
                text = '<h1 class="title">Title: Sample Paper</h1>'
                def raise_for_status(self): pass
            return R()

    resolved = resolve_paper(FakeSession(), "2408.03594")
    assert resolved.year == "2024"


def test_resolved_paper_year_none_for_local_pdf(tmp_path: Path) -> None:
    from paper_garden.download import resolve_paper

    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%EOF\n")

    resolved = resolve_paper(None, str(pdf))
    assert resolved.year is None
