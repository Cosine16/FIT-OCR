# ocr-server

Command-line OCR tool powered by **GLM-4V** (Zhipu AI / 智谱清言).

## Prerequisites

- Python 3.10+
- Zhipu AI API key — get one at [open.bigmodel.cn](https://open.bigmodel.cn)

## Quickstart

```bash
# Install dependencies
uv sync

# Set your API key
cp .env.example .env
# Edit .env and paste your key

# Run OCR on an image
uv run ocr-server image.png

# Or pass the key directly
uv run ocr-server -k YOUR_KEY image.png

# OCR a whole directory
uv run ocr-server ./screenshots/

# Save results to a file
uv run ocr-server -o output.txt image.png
```

## Usage

```
Usage: ocr-server [OPTIONS] PATHS...

  OCR text from images using Zhipu GLM-4V.

  PATHS can be one or more image files or directories to scan for images.

Options:
  -k, --api-key TEXT   Zhipu AI API key (or set ZHIPUAI_API_KEY env var).
  -m, --model TEXT     Model ID (default: glm-4v-plus).
  -o, --output PATH    Output file for results.
  -p, --prompt TEXT    Custom OCR prompt.
  -v, --verbose        Enable verbose logging.
  -q, --quiet          Suppress all output except errors.
  --help               Show this message and exit.
```

## Supported Image Formats

PNG, JPEG, BMP, GIF, WEBP, TIFF

Images larger than 2048×2048 pixels are automatically downscaled before sending.
