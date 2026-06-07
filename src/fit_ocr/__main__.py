"""CLI entry point: python -m fit_ocr"""
import uvicorn
from fit_ocr.infrastructure.config import Config


def main():
    cfg = Config.from_env()
    uvicorn.run(
        "fit_ocr.web.app:create_app",
        factory=True,
        host=cfg.host,
        port=cfg.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
