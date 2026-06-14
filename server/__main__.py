"""CLI entry point: python -m server"""
import uvicorn
from server.infrastructure.config import Config


def main():
    cfg = Config.from_env()
    uvicorn.run(
        "server.api.app:create_app",
        factory=True,
        host=cfg.host,
        port=cfg.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
