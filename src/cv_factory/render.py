"""Batch-render RenderCV YAML files to PDF. Non-interactive, CI-safe."""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

log = logging.getLogger("cv_factory")
YAML_SUFFIXES = {".yaml", ".yml"}


def output_name(yaml_path: Path, root: Path) -> str:
    """Path relative to root, joined with '_': options/x.yaml -> options_x.pdf"""
    try:
        rel = yaml_path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = Path(yaml_path.name)
    return "_".join(rel.with_suffix(".pdf").parts)


def render_one(yaml_path: Path, root: Path, output_dir: Path, work_dir: Path) -> Path:
    if not yaml_path.is_file():
        raise FileNotFoundError(yaml_path)
    name = output_name(yaml_path, root)
    pdf_path = (output_dir / name).resolve()
    cmd = [
        sys.executable, "-m", "rendercv", "render", str(yaml_path),
        "--output-folder", str((work_dir / name.removesuffix(".pdf")).resolve()),
        "--pdf-path", str(pdf_path),
        "-nomd", "-nohtml", "-nopng",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{yaml_path} failed:\n{result.stdout}\n{result.stderr}")
    if not pdf_path.is_file():
        raise RuntimeError(f"{yaml_path}: RenderCV exited 0 but no PDF at {pdf_path}")
    return pdf_path


def discover(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in YAML_SUFFIXES)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Render RenderCV YAML files to PDF.")
    parser.add_argument("files", nargs="*", type=Path, help="YAML files (default: all under --root)")
    parser.add_argument("--root", type=Path, default=Path("cvs"))
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--work-dir", type=Path, default=Path("build"))
    args = parser.parse_args(argv)

    files = args.files or discover(args.root)
    if not files:
        log.error("No YAML files found (root=%s).", args.root)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for yaml_path in files:
        try:
            log.info("OK %s", render_one(yaml_path, args.root, args.output_dir, args.work_dir))
        except (FileNotFoundError, OSError, RuntimeError) as exc:  # report per-file failures
            failures += 1
            log.error("%s", exc)
    log.info("%d rendered, %d failed", len(files) - failures, failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
