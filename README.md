# FIT-OCR

Photo-to-LaTeX OCR with local/cloud fallback.

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,cloud]"

# Download models
bash scripts/fetch_models.sh

# Run
fit-ocr
# or
python -m fit_ocr
```

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
