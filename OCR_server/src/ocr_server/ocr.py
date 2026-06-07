"""OCR engine using Zhipu AI GLM-4V model."""

import base64
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from zhipuai import ZhipuAI

logger = logging.getLogger(__name__)

# Maximum image size before downscaling (long edge in pixels)
MAX_IMAGE_SIZE = 2048
# Maximum image file size in bytes (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def _encode_image(image_path: Path) -> str:
    """Load an image, optionally downscale, and return a base64 data-URL string."""
    img = Image.open(image_path)

    # Downscale if the image is too large
    if max(img.size) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        logger.info("Downscaling image from %s → %s", img.size, new_size)
        img = img.resize(new_size, Image.LANCZOS)

    buf = BytesIO()
    fmt = img.format or "PNG"
    img.save(buf, format=fmt)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{data}"


def recognize_image(
    image_path: Path,
    api_key: str,
    model: str = "glm-4v-plus",
    prompt: Optional[str] = None,
) -> str:
    """Send an image to GLM-4V for OCR and return the recognized text.

    Args:
        image_path: Path to the image file.
        api_key: Zhipu AI API key.
        model: Model ID to use (default ``glm-4v-plus``).
        prompt: Custom prompt; if ``None``, a default OCR prompt is used.

    Returns:
        The recognized text string.
    """
    if prompt is None:
        prompt = (
            "请对这张图片进行OCR识别，将图片中的所有文字内容提取出来。"
            "保持原有的格式和排版，包括表格结构。"
            "如果图片中有公式，请用LaTeX格式输出。"
        )

    client = ZhipuAI(api_key=api_key)
    b64_url = _encode_image(image_path)

    logger.info("Calling model=%s for image=%s", model, image_path.name)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": b64_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    text = response.choices[0].message.content
    logger.info("OCR completed, %d characters returned", len(text))
    return text


def recognize_images_batch(
    image_paths: list[Path],
    api_key: str,
    model: str = "glm-4v-plus",
    prompt: Optional[str] = None,
    verbose: bool = False,
) -> dict[Path, str]:
    """Run OCR on multiple images sequentially.

    Returns:
        A dict mapping each image path to its recognized text.
    """
    results: dict[Path, str] = {}
    total = len(image_paths)
    for i, path in enumerate(image_paths, 1):
        if verbose:
            logger.info("[%d/%d] Processing: %s", i, total, path.name)
        try:
            text = recognize_image(path, api_key=api_key, model=model, prompt=prompt)
            results[path] = text
        except Exception:
            logger.exception("Failed to OCR image: %s", path)
            results[path] = ""
    return results
