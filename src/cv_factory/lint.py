"""Text-level checks for RenderCV YAML files. RenderCV still owns schema validation."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

YAML_SUFFIXES = {".yaml", ".yml"}
STRICT_DATE_KEY = re.compile(r"^\s*(?:-\s+)?(start_date|end_date):\s*(.*?)\s*$")
VALID_DATE = re.compile(r"""^(["']?)(\d{4}(-\d{2}(-\d{2})?)?|present)\1$""")
BLOCK_SCALAR = re.compile(r"(:|^\s*-)\s*[>|][-+]?\s*$")
ERROR_RULES = [
    ("AI citation artifact", re.compile(r"【|†")),
    ("non-breaking space", re.compile("\u00a0")),
]
WARNING_RULES = [
    ("raw < or > (renders OK on RenderCV 2.8, review wording)", re.compile(r"[<>]")),
]


@dataclass(frozen=True)
class Finding:
    severity: str
    path: Path
    line: int
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.severity} {self.path}:{self.line}: {self.rule}: {self.text.strip()[:100]}"


def lint_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for rule, pattern in ERROR_RULES:
            if pattern.search(line):
                findings.append(Finding("ERROR", path, lineno, rule, line))
        if not BLOCK_SCALAR.search(line):
            for rule, pattern in WARNING_RULES:
                if pattern.search(line):
                    findings.append(Finding("WARN", path, lineno, rule, line))
        match = STRICT_DATE_KEY.match(line)
        if match and match.group(2) and not VALID_DATE.match(match.group(2)):
            findings.append(Finding("ERROR", path, lineno, "date not YYYY-MM or present", line))
    return findings


def expand(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(x for x in p.rglob("*") if x.is_file() and x.suffix in YAML_SUFFIXES))
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(p)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint RenderCV YAML files.")
    parser.add_argument("paths", nargs="+", type=Path, help="files or folders")
    files = expand(parser.parse_args(argv).paths)
    findings = [f for p in files for f in lint_file(p)]
    for finding in findings:
        print(finding)
    errors = sum(f.severity == "ERROR" for f in findings)
    print(f"{len(files)} file(s), {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
