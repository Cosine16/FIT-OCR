"""pytest fixtures for FIT-OCR tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from server.engines.local import LocalEngine
from server.engines.cloud import CloudEngine
from server.engines.fallback import FallbackEngine


@pytest.fixture(scope="session")
def sample_image() -> Path:
    return Path(__file__).parent.parent / "samples" / "synthetic_math.png"


@pytest.fixture
def local_engine() -> LocalEngine:
    return LocalEngine(device="cpu", enable_table=False)


@pytest.fixture
def cloud_engine() -> CloudEngine | None:
    """Returns CloudEngine if API key available, else None."""
    import os

    key = os.getenv("ZHIPUAI_API_KEY")
    if not key:
        pytest.skip("ZHIPUAI_API_KEY not set")
    return CloudEngine(api_key=key)


@pytest.fixture
def fallback_engine(local_engine, cloud_engine) -> FallbackEngine:
    return FallbackEngine(local=local_engine, cloud=cloud_engine)
