from pathlib import Path

from paper_garden.extract import find_extracted_files


def test_find_extracted_files_prefers_main_markdown_and_json(tmp_path: Path) -> None:
    extracted_dir = tmp_path / "extracted"
    extracted_dir.mkdir()
    (extracted_dir / "document.md").write_text("body", encoding="utf-8")
    (extracted_dir / "document.json").write_text("{}", encoding="utf-8")

    result = find_extracted_files(extracted_dir)

    assert result.markdown_path == extracted_dir / "document.md"
    assert result.json_path == extracted_dir / "document.json"
