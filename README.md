# FIT-OCR

Photo-to-LaTeX OCR with local/cloud fallback.

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate

# CPU-only torch (recommended for low-VRAM GPUs like GTX 1650 4GB).
# Skip this line if you want CUDA torch and have >=8GB VRAM.
pip install torch==2.5.1+cpu torchvision==0.20.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Project + dev + cloud extras
pip install -e ".[dev,cloud]"

# Download models (~1.5GB; uses HuggingFace mirror friendly to CN networks)
bash scripts/fetch_models.sh

# Run
fit-ocr
# or
python -m fit_ocr
```

> **Note on dependency pins:** `transformers`, `tokenizers`, `optimum`, and
> `onnxruntime` are pinned in `pyproject.toml` because `pix2text 1.1.x` only
> works with this combination. Do not bump them blindly.

## Architecture

```
src/fit_ocr/
├── core/           # Domain layer (models, interfaces, exceptions)
├── engines/        # Local (Pix2Text), Cloud (GLM-4V), Fallback
├── infrastructure/ # Config, logging
└── web/            # FastAPI app
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEVICE` | `cpu` | torch device |
| `ZHIPUAI_API_KEY` | — | GLM-4V API key |
| `PORT` | `8001` | Web server port |

## License

MIT
