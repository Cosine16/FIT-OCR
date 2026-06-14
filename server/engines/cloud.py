"""Cloud OCR engine using Zhipu AI GLM-4V."""
from __future__ import annotations

import base64
import logging
import os
import time
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image

from server.core.interfaces import OCREngine
from server.core.models import OCRResult
from server.core.exceptions import OCRError, EngineNotAvailableError

logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE = 2048


def _encode_image(image_path: Path) -> str:
    img = Image.open(image_path)
    if max(img.size) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    buf = BytesIO()
    fmt = img.format or "PNG"
    img.save(buf, format=fmt)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{data}"


class CloudEngine(OCREngine):
    """GLM-4V cloud engine (requires API key, higher accuracy)."""

    name = "glm-4v-cloud"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4v-plus",
        prompt: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        self.model = model
        self.prompt = prompt or (
            "请对这张图片进行OCR识别，将图片中的所有文字内容提取出来。"
            "保持原有的格式和排版，包括表格结构。"
            "如果图片中有公式，请用LaTeX格式输出。"
        )

    def recognize(self, image_path: str | Path) -> OCRResult:
        if not self.api_key:
            raise EngineNotAvailableError("ZHIPUAI_API_KEY not set")

        try:
            from zhipuai import ZhipuAI
        except ImportError as e:
            raise OCRError("zhipuai not installed") from e

        client = ZhipuAI(api_key=self.api_key)
        b64_url = _encode_image(Path(image_path))

        logger.info("[cloud] calling %s for %s", self.model, Path(image_path).name)
        t0 = time.time()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": b64_url}},
                        {"type": "text", "text": self.prompt},
                    ],
                }
            ],
        )
        text = response.choices[0].message.content
        elapsed = time.time() - t0
        logger.info("[cloud] returned %d chars in %.1fs", len(text), elapsed)
        return OCRResult(
            text=text,
            engine=self.name,
            elapsed_s=elapsed,
            image_path=Path(image_path),
        )
