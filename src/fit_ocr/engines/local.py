"""Local OCR engine using Pix2Text."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from fit_ocr.core.interfaces import OCREngine
from fit_ocr.core.models import OCRResult
from fit_ocr.core.exceptions import OCRError

logger = logging.getLogger(__name__)


class LocalEngine(OCREngine):
    """Pix2Text local engine (offline, privacy-preserving)."""

    name = "pix2text-local"

    def __init__(self, device: str = "cpu", enable_table: bool = False):
        self.device = device
        self.enable_table = enable_table
        self._p2t: Optional[object] = None

    def _load(self):
        if self._p2t is None:
            try:
                from pix2text import Pix2Text
            except ImportError as e:
                raise OCRError("pix2text not installed") from e

            logger.info("[local] loading Pix2Text (device=%s)...", self.device)
            self._p2t = Pix2Text.from_config(
                device=self.device, enable_table=self.enable_table
            )
            logger.info("[local] Pix2Text loaded")
        return self._p2t

    def recognize(self, image_path: str | Path) -> OCRResult:
        p2t = self._load()
        t0 = time.time()
        text = p2t.recognize(str(image_path), file_type="text")
        elapsed = time.time() - t0
        return OCRResult(
            text=text if isinstance(text, str) else "",
            engine=self.name,
            elapsed_s=elapsed,
            image_path=Path(image_path),
        )
