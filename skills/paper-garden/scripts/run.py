#!/usr/bin/env python3
"""Full ingest pipeline (standalone use). For skill-driven use, see download.py + finalize.py."""
import sys
from pathlib import Path

_repo_src = Path(__file__).resolve().parents[3] / "src"
if _repo_src.is_dir() and str(_repo_src) not in sys.path:
    sys.path.insert(0, str(_repo_src))

from paper_garden.ingest import main

if __name__ == "__main__":
    raise SystemExit(main())
