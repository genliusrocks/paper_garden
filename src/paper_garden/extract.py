from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class ExtractionResult:
    markdown_path: Path
    json_path: Path


def find_extracted_files(extracted_dir: Path) -> ExtractionResult:
    markdown_candidates = sorted(extracted_dir.rglob("*.md"))
    json_candidates = sorted(extracted_dir.rglob("*.json"))
    if not markdown_candidates:
        raise FileNotFoundError(f"No markdown files found under {extracted_dir}")
    if not json_candidates:
        raise FileNotFoundError(f"No JSON files found under {extracted_dir}")

    preferred_markdown = [
        path for path in markdown_candidates if path.name.lower() in {"document.md", "output.md"}
    ]
    preferred_json = [
        path for path in json_candidates if path.name.lower() in {"document.json", "output.json"}
    ]

    return ExtractionResult(
        markdown_path=preferred_markdown[0] if preferred_markdown else markdown_candidates[0],
        json_path=preferred_json[0] if preferred_json else json_candidates[0],
    )


def run_marker(pdf_path: Path, paper_dir: Path) -> ExtractionResult:
    extracted_dir = paper_dir / "extracted"
    extracted_dir.mkdir(exist_ok=True)
    subprocess.run(
        [
            "uvx",
            "--from",
            "marker-pdf",
            "marker_single",
            str(pdf_path),
            "--output_dir",
            str(extracted_dir),
        ],
        check=True,
    )
    return find_extracted_files(extracted_dir)
