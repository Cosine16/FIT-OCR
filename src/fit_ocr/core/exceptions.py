"""Custom exceptions for FIT-OCR."""


class OCRError(Exception):
    """Base exception for OCR failures."""

    pass


class EngineNotAvailableError(OCRError):
    """Raised when an engine is not available (e.g., missing API key)."""

    pass
