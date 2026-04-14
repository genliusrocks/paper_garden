from __future__ import annotations

import re
from pathlib import Path


ID_RE = re.compile(r"^- `pg-(\d{4})-([0-9a-f]{5})`")


def parse_existing_seqs(index_path: Path) -> list[int]:
    if not index_path.is_file():
        return []
    seqs: list[int] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = ID_RE.match(line)
        if m:
            seqs.append(int(m.group(2), 16))
    return seqs
