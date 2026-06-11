"""SQLAlchemy ORM models for FIT-OCR admin."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Base(DeclarativeBase):
    pass


class RecordStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class OCRRecord(Base):
    """Each OCR recognition call is one record."""

    __tablename__ = "ocr_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    engine: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[RecordStatus] = mapped_column(
        SAEnum(RecordStatus), nullable=False, default=RecordStatus.SUCCESS
    )
    result_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    result_text_preview: Mapped[str | None] = mapped_column(String(500), nullable=True)
    elapsed_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    image_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "image_filename": self.image_filename,
            "engine": self.engine,
            "status": self.status.value,
            "result_path": self.result_path,
            "result_text_preview": self.result_text_preview,
            "elapsed_ms": self.elapsed_ms,
            "image_size_bytes": self.image_size_bytes,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }


class AdminUser(Base):
    """Admin panel user for JWT authentication."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
