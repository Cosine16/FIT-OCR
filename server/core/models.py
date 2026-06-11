"""Domain models for FIT-OCR."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class OCRResult:
    """Result of an OCR operation."""

    text: str
    engine: str
    elapsed_s: float
    image_path: Optional[Path] = None

    def __post_init__(self):
        object.__setattr__(
            self, "image_path", Path(self.image_path) if self.image_path else None
        )
