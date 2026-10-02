from pathlib import Path

from cv_factory.lint import expand, lint_file


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "cv.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def rules(path: Path) -> list[tuple[str, str]]:
    return [(f.severity, f.rule) for f in lint_file(path)]


def test_clean_file_has_no_findings(tmp_path):
    assert rules(write(tmp_path, "start_date: 2023-10\nend_date: present\n")) == []


def test_text_date_is_error(tmp_path):
    assert rules(write(tmp_path, "  - start_date: Oct 2023\n")) == [("ERROR", "date not YYYY-MM or present")]


def test_free_text_date_key_is_allowed(tmp_path):
    assert rules(write(tmp_path, "date: Fall 2023\n")) == []


def test_ai_citation_is_error(tmp_path):
    assert ("ERROR", "AI citation artifact") in rules(write(tmp_path, 'summary: "Built it【0†source】"\n'))


def test_comparison_symbol_is_warning_only(tmp_path):
    found = rules(write(tmp_path, '- "Kept <3% variance"\n'))
    assert [severity for severity, _ in found] == ["WARN"]


def test_folded_block_marker_is_not_flagged(tmp_path):
    assert rules(write(tmp_path, "summary:\n  - >\n    plain text\n")) == []


def test_comment_lines_are_ignored(tmp_path):
    assert rules(write(tmp_path, "# start_date: Oct 2023 > draft\n")) == []


def test_expand_finds_nested_yaml(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.yaml").write_text("x: 1\n")
    (tmp_path / "sub" / "b.yml").write_text("x: 1\n")
    (tmp_path / "notes.txt").write_text("x\n")
    assert [p.name for p in expand([tmp_path])] == ["a.yaml", "b.yml"]
