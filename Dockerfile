# ---- base: pinned runtime dependencies (cached layer) ----
FROM python:3.12.15-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    TYPST_CACHE_DIR=/tmp/typst-cache \
    PYTHONPATH=/opt/cv-factory/src

RUN pip install --no-cache-dir "rendercv[full]==2.8"

# ---- test: lint + unit + smoke render; build fails if any check fails ----
FROM base AS test

RUN pip install --no-cache-dir "pytest==9.1.1" "ruff==0.16.10"
WORKDIR /opt/cv-factory
COPY pyproject.toml ./
COPY src/ src/
COPY tests/ tests/
COPY examples/ examples/
RUN python -m ruff check src tests \
 && python -m cv_factory.lint examples \
 && python -m pytest -q

# ---- runtime: default target, non-root ----
FROM base AS runtime

COPY src/ /opt/cv-factory/src/
RUN useradd --create-home --uid 1000 cv
USER cv
WORKDIR /work

ENTRYPOINT ["python", "-m", "cv_factory.render"]
