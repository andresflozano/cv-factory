import shutil
from pathlib import Path

from cv_factory.render import discover, output_name, render_one

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "John_Doe_CV.yaml"


def test_output_name_flattens_subfolders(tmp_path):
    root = tmp_path / "cvs"
    assert output_name(root / "options" / "x.yaml", root) == "options_x.pdf"
    assert output_name(root / "x.yml", root) == "x.pdf"


def test_output_name_outside_root_uses_file_name(tmp_path):
    assert output_name(tmp_path / "elsewhere" / "x.yaml", tmp_path / "cvs") == "x.pdf"


def test_discover_ignores_non_yaml(tmp_path):
    (tmp_path / "a.yaml").write_text("x: 1\n")
    (tmp_path / "b.txt").write_text("x\n")
    assert [p.name for p in discover(tmp_path)] == ["a.yaml"]


def test_example_renders_to_pdf(tmp_path):
    """Smoke test: real RenderCV call on fake data. Needs the container (rendercv + network for Typst packages)."""
    root = tmp_path / "cvs"
    root.mkdir()
    shutil.copy(EXAMPLE, root / EXAMPLE.name)
    pdf = render_one(root / EXAMPLE.name, root, tmp_path / "dist", tmp_path / "build")
    assert pdf.name == "John_Doe_CV.pdf"
    assert pdf.read_bytes()[:5] == b"%PDF-"
