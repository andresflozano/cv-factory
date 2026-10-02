# cv-factory

Containerized, non-interactive renderer for [RenderCV](https://github.com/rendercv/rendercv) YAML files. CV content lives in YAML; this repo owns the rendering engine, quality checks, and the pinned toolchain.

## Why

- **Reproducible:** Python and RenderCV are pinned to reduce version drift between builds.
- **CI-safe:** no prompts; every file is rendered, failures are reported per file, and the exit code is nonzero if any fail.
- **Checked:** a linter catches common YAML problems before RenderCV runs; tests and a smoke render run during the image build.
- **Data separated from engine:** personal YAMLs are not stored in this repo.

## Usage

```bash
docker build -t cv-factory .

# Render every YAML under ./cvs into ./dist
docker run --rm -v "$PWD":/work -u "$(id -u):$(id -g)" cv-factory

# Other folder or specific files
docker run --rm -v "$PWD":/work -u "$(id -u):$(id -g)" cv-factory --root inputs
docker run --rm -v "$PWD":/work -u "$(id -u):$(id -g)" cv-factory cvs/me/data-engineer.en.yaml

# Lint only
docker run --rm -v "$PWD":/work --entrypoint python cv-factory -m cv_factory.lint cvs
```

Output names flatten subfolders: `cvs/options/blue.yaml` becomes `dist/options_blue.pdf`. RenderCV intermediate files go to `build/`.

## Lint rules

| Severity | Rule |
|---|---|
| Error | `start_date` / `end_date` not `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `present` |
| Error | AI citation artifacts (`【…†source】`) |
| Error | Non-breaking spaces |
| Warning | Raw `<` or `>` in text (renders correctly on RenderCV 2.8; flagged for wording review) |

The free-text `date` key is not checked. RenderCV remains the schema validator.

## Development

```bash
# Lint, unit tests, and a smoke render of examples/ (fake data); build fails on any failure
docker build --target test .
```

| Path | Purpose |
|---|---|
| `src/cv_factory/render.py` | Batch renderer (container entrypoint) |
| `src/cv_factory/lint.py` | YAML text checks |
| `tests/` | Unit tests and smoke render |
| `examples/` | Fake-data CV used by the smoke test |

## Requirements

Docker Engine (Linux or WSL 2). Docker Desktop is not required.

## License

Apache-2.0. Copyright 2026 Andres Lozano.
