from pathlib import Path

from paper_garden.download import DownloadedPaper
from paper_garden.extract import ExtractionResult
from paper_garden.config import ConfigurationRequiredError
from paper_garden.ingest import write_metadata


def test_write_metadata_creates_metadata_file(tmp_path: Path) -> None:
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()

    metadata_path = write_metadata(
        paper_dir=paper_dir,
        arxiv_id="2501.01234",
        title="Paper Title",
        source_ref="https://arxiv.org/abs/2501.01234",
        source_kind="arxiv",
        language="en",
        tags=["rag"],
    )

    text = metadata_path.read_text(encoding="utf-8")
    assert 'arxiv_id = "2501.01234"' in text
    assert 'language = "en"' in text
    assert 'source_kind = "arxiv"' in text
    assert 'source_ref = "https://arxiv.org/abs/2501.01234"' in text


def test_main_runs_end_to_end_with_stubbed_dependencies(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\nlanguage = "en"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def fake_download_paper(session, input_value: str, papers_dir: Path) -> DownloadedPaper:
        paper_dir = papers_dir / "2501.01234_test_title"
        paper_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = paper_dir / "paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        return DownloadedPaper(
            arxiv_id="2501.01234",
            title="Test Title",
            paper_slug="2501.01234_test_title",
            pdf_path=pdf_path,
            source_kind="arxiv",
            source_ref="https://arxiv.org/abs/2501.01234",
        )

    def fake_run_marker(pdf_path: Path, paper_dir: Path) -> ExtractionResult:
        extracted_dir = paper_dir / "extracted"
        extracted_dir.mkdir(exist_ok=True)
        markdown_path = extracted_dir / "document.md"
        json_path = extracted_dir / "document.json"
        markdown_path.write_text("# Body", encoding="utf-8")
        json_path.write_text("{}", encoding="utf-8")
        return ExtractionResult(markdown_path=markdown_path, json_path=json_path)

    monkeypatch.setattr("paper_garden.ingest.download_paper", fake_download_paper)
    monkeypatch.setattr("paper_garden.ingest.run_marker", fake_run_marker)

    from paper_garden.ingest import main

    rc = main(["2501.01234", "--config", str(config_path)])

    garden_dir = tmp_path / "garden"
    assert rc == 0
    assert (garden_dir / "index.md").is_file()
    assert (garden_dir / "tags" / "arxiv.md").is_file()
    assert (garden_dir / "papers" / "2501.01234_test_title" / "metadata.toml").is_file()


def test_main_accepts_explicit_tags(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text('garden_dir = "./garden"\nlanguage = "en"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def fake_download_paper(session, input_value: str, papers_dir: Path) -> DownloadedPaper:
        paper_dir = papers_dir / "2501.01234_test_title"
        paper_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = paper_dir / "paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        return DownloadedPaper(
            arxiv_id="2501.01234",
            title="Test Title",
            paper_slug="2501.01234_test_title",
            pdf_path=pdf_path,
            source_kind="arxiv",
            source_ref="https://arxiv.org/abs/2501.01234",
        )

    def fake_run_marker(pdf_path: Path, paper_dir: Path) -> ExtractionResult:
        extracted_dir = paper_dir / "extracted"
        extracted_dir.mkdir(exist_ok=True)
        markdown_path = extracted_dir / "document.md"
        json_path = extracted_dir / "document.json"
        markdown_path.write_text("# Body", encoding="utf-8")
        json_path.write_text("{}", encoding="utf-8")
        return ExtractionResult(markdown_path=markdown_path, json_path=json_path)

    monkeypatch.setattr("paper_garden.ingest.download_paper", fake_download_paper)
    monkeypatch.setattr("paper_garden.ingest.run_marker", fake_run_marker)

    from paper_garden.ingest import main

    rc = main(["2501.01234", "--config", str(config_path), "--tags", "rag,transformer"])

    garden_dir = tmp_path / "garden"
    assert rc == 0
    assert (garden_dir / "tags" / "rag.md").is_file()
    assert (garden_dir / "tags" / "transformer.md").is_file()
    assert not (garden_dir / "tags" / "arxiv.md").exists()


def test_main_requires_configuration_before_running(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "paper_garden.toml"
    config_path.write_text(
        '# Run:\n# uv run python skills/paper-garden/scripts/configure.py --garden-dir "./paper_garden" --language "en"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    from paper_garden.ingest import main

    try:
        main(["2501.01234", "--config", str(config_path)])
    except ConfigurationRequiredError as exc:
        assert "configure.py" in str(exc)
    else:
        raise AssertionError("Expected ConfigurationRequiredError")
