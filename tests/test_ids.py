from pathlib import Path

from paper_garden.ids import ID_RE, parse_existing_seqs


def test_id_re_matches_valid_index_line() -> None:
    line = "- `pg-2024-00a3f` [Title](papers/x/wiki.md) | tags: foo"
    m = ID_RE.match(line)
    assert m is not None
    assert m.group(1) == "2024"
    assert m.group(2) == "00a3f"


def test_id_re_does_not_match_old_format() -> None:
    line = "- (2024) [Title](papers/x/wiki.md) | tags: foo"
    assert ID_RE.match(line) is None


def test_parse_existing_seqs_empty_file(tmp_path: Path) -> None:
    index = tmp_path / "index.md"
    index.write_text("# Paper Garden\n\n## Papers\n\n", encoding="utf-8")
    assert parse_existing_seqs(index) == []


def test_parse_existing_seqs_extracts_hex5(tmp_path: Path) -> None:
    index = tmp_path / "index.md"
    index.write_text(
        "# Paper Garden\n\n## Papers\n\n"
        "- `pg-2017-00001` [Paper A](papers/a/wiki.md) | tags: x\n"
        "- `pg-2024-00a3f` [Paper B](papers/b/wiki.md) | tags: y\n"
        "- `pg-2003-1b2c4` [Paper C](papers/c/wiki.md) | tags: z\n",
        encoding="utf-8",
    )
    assert sorted(parse_existing_seqs(index)) == [0x00001, 0x00a3f, 0x1b2c4]


def test_parse_existing_seqs_ignores_malformed_lines(tmp_path: Path) -> None:
    index = tmp_path / "index.md"
    index.write_text(
        "- `pg-2024-00001` [Good](papers/a/wiki.md)\n"
        "- (2024) [Old format](papers/b/wiki.md)\n"
        "- `pg-2024-GGGGG` [Bad hex](papers/c/wiki.md)\n"
        "- `pg-99-001` [Bad year](papers/d/wiki.md)\n",
        encoding="utf-8",
    )
    assert parse_existing_seqs(index) == [1]


def test_parse_existing_seqs_missing_file(tmp_path: Path) -> None:
    assert parse_existing_seqs(tmp_path / "nonexistent.md") == []
