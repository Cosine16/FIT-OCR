"""OCR engine implementations."""
from .local import LocalEngine
from .cloud import CloudEngine
from .fallback import FallbackEngine

__all__ = ["LocalEngine", "CloudEngine", "FallbackEngine"]
