"""Unit tests for OCR engines."""
from __future__ import annotations

from pathlib import Path

from server.core.models import OCRResult
from server.core.exceptions import EngineNotAvailableError
from server.engines.local import LocalEngine
from server.engines.cloud import CloudEngine


def test_local_engine_recognizes(sample_image: Path):
    eng = LocalEngine(device="cpu", enable_table=False)
    result = eng.recognize(sample_image)
    assert isinstance(result, OCRResult)
    assert result.engine == "pix2text-local"
    assert len(result.text) > 0
    assert "Theorem" in result.text or "Euler" in result.text


def test_cloud_engine_without_key_raises():
    eng = CloudEngine(api_key=None)
    try:
        eng.recognize("nonexistent.png")
        assert False, "should have raised"
    except EngineNotAvailableError:
        pass
