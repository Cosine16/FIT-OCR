"""Fallback engine: try local first, fallback to cloud on failure."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from server.core.interfaces import OCREngine
from server.core.models import OCRResult
from server.core.exceptions import OCRError

logger = logging.getLogger(__name__)


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

    def recognize(self, image_path: str | Path) -> OCRResult:
        path = Path(image_path)

        # 1. Try local
        if self.local:
            try:
                logger.info("[fallback] trying local engine: %s", self.local.name)
                t0 = time.time()
                result = self.local.recognize(path)
                logger.info(
                    "[fallback] local ok in %.1fs (%d chars)",
                    result.elapsed_s,
                    len(result.text),
                )
                return result
            except Exception as e:
                logger.warning("[fallback] local failed: %s", e)

        # 2. Fallback to cloud
        if self.cloud:
            try:
                logger.info("[fallback] trying cloud engine: %s", self.cloud.name)
                result = self.cloud.recognize(path)
                logger.info(
                    "[fallback] cloud ok in %.1fs (%d chars)",
                    result.elapsed_s,
                    len(result.text),
                )
                return result
            except Exception as e:
                logger.error("[fallback] cloud also failed: %s", e)
                raise OCRError(f"Both local and cloud OCR failed: {e}") from e

        raise OCRError("No OCR engine available")
