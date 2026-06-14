# ── Multi-stage Dockerfile for FIT-OCR ──────────────────────────────────────
# Stage 1: build (optional — currently source-only, no compilation needed)
# Stage 2: runtime

FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="FIT-OCR"
LABEL org.opencontainers.image.description="Photo-to-LaTeX OCR with local/cloud fallback"
LABEL org.opencontainers.image.version="0.1.0"

# ── System deps ─────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Python env ──────────────────────────────────────────────────────────────
WORKDIR /app

COPY pyproject.toml README.md ./
COPY server/ server/

# Install fit-ocr in non-editable mode (cloud deps optional, torch pulled by pix2text)
RUN pip install --no-cache-dir ".[cloud]" \
    && python -c "import server; print(server.__version__)"

# ── Data volume mounts ──────────────────────────────────────────────────────
RUN mkdir -p /app/data/uploads /app/data/output

# ── Runtime ─────────────────────────────────────────────────────────────────
EXPOSE 8001

ENV HOST=0.0.0.0
ENV PORT=8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health')"

CMD ["uvicorn", "server.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001", "--no-access-log"]
