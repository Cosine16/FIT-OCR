"""Local OCR engine using Pix2Text."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from engines import OCREngine

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
            from pix2text import Pix2Text

            logger.info("[local] loading Pix2Text (device=%s)...", self.device)
            self._p2t = Pix2Text.from_config(
                device=self.device, enable_table=self.enable_table
            )
            logger.info("[local] Pix2Text loaded")
        return self._p2t

    def recognize(self, image_path: str | Path) -> str:
        p2t = self._load()
        text = p2t.recognize(str(image_path), file_type="text")
        # file_type="text" returns str directly
        return text if isinstance(text, str) else ""
