"""12-Factor configuration — env vars over hard-coded values."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Application configuration from environment."""

    device: str = "cpu"
    enable_table: bool = False
    zhipu_api_key: str | None = None
    cloud_model: str = "glm-4v-plus"
    upload_dir: Path = Path("data/uploads")
    output_dir: Path = Path("data/output")
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            device=os.getenv("DEVICE", "cpu"),
            enable_table=os.getenv("ENABLE_TABLE", "").lower() in ("1", "true", "yes"),
            zhipu_api_key=os.getenv("ZHIPUAI_API_KEY") or None,
            cloud_model=os.getenv("CLOUD_MODEL", "glm-4v-plus"),
            upload_dir=Path(os.getenv("UPLOAD_DIR", "data/uploads")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "data/output")),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8001")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
