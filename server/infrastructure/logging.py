"""Structured logging setup."""
import logging
import sys


def setup_logging(level: str = "INFO"):
    """Configure root logger with consistent formatting."""
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
