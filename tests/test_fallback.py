"""Integration tests for fallback engine."""
from __future__ import annotations

from pathlib import Path

from server.core.models import OCRResult
from server.core.exceptions import OCRError
from server.engines.local import LocalEngine
from server.engines.cloud import CloudEngine
from server.engines.fallback import FallbackEngine


def test_fallback_uses_local_when_available(sample_image: Path):
    local = LocalEngine(device="cpu", enable_table=False)
    fallback = FallbackEngine(local=local, cloud=None)
    result = fallback.recognize(sample_image)
    assert isinstance(result, OCRResult)
    assert result.engine == "pix2text-local"


def test_fallback_raises_when_both_fail(sample_image: Path):
    class BrokenLocal(LocalEngine):
        name = "broken-local"

        def recognize(self, image_path):
            raise RuntimeError("LOCAL DOWN")

    class BrokenCloud(CloudEngine):
        name = "broken-cloud"

        def recognize(self, image_path):
            raise RuntimeError("CLOUD DOWN")

    fallback = FallbackEngine(local=BrokenLocal(), cloud=BrokenCloud())
    try:
        fallback.recognize(sample_image)
        assert False, "should have raised"
    except OCRError as e:
        assert "Both local and cloud OCR failed" in str(e)
