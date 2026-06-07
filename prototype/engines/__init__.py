"""Unified OCR engine interface with local/cloud fallback."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class OCREngine:
    """Abstract base for OCR engines."""

    name: str = "abstract"

    def recognize(self, image_path: str | Path) -> str:
        raise NotImplementedError


class FallbackEngine(OCREngine):
    """Try local first, fallback to cloud on failure."""

    name = "fallback(local→cloud)"

    def __init__(
        self,
        local: Optional[OCREngine] = None,
        cloud: Optional[OCREngine] = None,
        timeout_s: float = 30.0,
    ):
        self.local = local
        self.cloud = cloud
        self.timeout_s = timeout_s

    def recognize(self, image_path: str | Path) -> str:
        path = Path(image_path)

        # 1. Try local
        if self.local:
            try:
                logger.info("[fallback] trying local engine: %s", self.local.name)
                t0 = time.time()
                text = self.local.recognize(path)
                logger.info(
                    "[fallback] local ok in %.1fs (%d chars)",
                    time.time() - t0,
                    len(text),
                )
                return text
            except Exception as e:
                logger.warning("[fallback] local failed: %s", e)

        # 2. Fallback to cloud
        if self.cloud:
            try:
                logger.info("[fallback] trying cloud engine: %s", self.cloud.name)
                t0 = time.time()
                text = self.cloud.recognize(path)
                logger.info(
                    "[fallback] cloud ok in %.1fs (%d chars)",
                    time.time() - t0,
                    len(text),
                )
                return text
            except Exception as e:
                logger.error("[fallback] cloud also failed: %s", e)
                raise RuntimeError(f"Both local and cloud OCR failed: {e}") from e

        raise RuntimeError("No OCR engine available")
