"""Abstract interfaces for OCR engines."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import OCRResult


class OCREngine(ABC):
    """Abstract base for all OCR engines."""

    name: str = "abstract"

    @abstractmethod
    def recognize(self, image_path: str | Path) -> OCRResult:
        """Recognize text in an image and return structured result."""
        ...
