"""Core domain layer — pure business logic, no external dependencies."""
from .models import OCRResult
from .interfaces import OCREngine
from .exceptions import OCRError, EngineNotAvailableError

__all__ = ["OCRResult", "OCREngine", "OCRError", "EngineNotAvailableError"]
