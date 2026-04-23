# ============================================================
# LP Solver Benchmark - Docker Image
# Uses Poetry, Alpine Python (lightweight)
# ============================================================

# ----- Stage 1: Build -----
FROM python:3.14-alpine AS builder

WORKDIR /build

RUN apk add --no-cache \
    gcc g++ musl-dev linux-headers

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# ----- Stage 2: Runtime -----
FROM python:3.14-alpine

WORKDIR /app

RUN apk add --no-cache libgcc libgomp && \
    adduser -D -u 1000 appuser

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser data/ ./data/

USER appuser
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]