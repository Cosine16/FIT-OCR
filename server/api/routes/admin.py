"""Admin API routes — authentication, records, stats."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from server.api.middleware.auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
)
from server.infrastructure.database import get_session
from server.infrastructure.models import AdminUser, OCRRecord, RecordStatus
from server.infrastructure.config import Config

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecordOut(BaseModel):
    id: int
    image_filename: str
    engine: str
    status: str
    result_path: str | None
    result_text_preview: str | None
    elapsed_ms: float
    image_size_bytes: int
    error_message: str | None
    created_at: str

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list[RecordOut]
    total: int
    page: int
    page_size: int


class StatsOverview(BaseModel):
    total_calls: int
    success_count: int
    failure_count: int
    avg_elapsed_ms: float


class TrendPoint(BaseModel):
    date: str
    count: int


class EngineStat(BaseModel):
    engine: str
    count: int
    pct: float


class BatchDeleteRequest(BaseModel):
    ids: list[int]


class CreateUserRequest(BaseModel):
    username: str
    password: str


# ── Auth ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_session)):
    user = db.query(AdminUser).filter(AdminUser.username == body.username).first()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user.username)
    return LoginResponse(access_token=token)


# ── Records ──────────────────────────────────────────────────────────────────

@router.get("/records", response_model=PaginatedResponse)
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    engine: str | None = Query(None, description="Filter by engine name"),
    status: str | None = Query(None, description="success or failure"),
    date_from: str | None = Query(None, description="ISO date, e.g. 2026-06-01"),
    date_to: str | None = Query(None, description="ISO date, e.g. 2026-06-11"),
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    q = db.query(OCRRecord)

    if engine:
        q = q.filter(OCRRecord.engine == engine)
    if status:
        try:
            st = RecordStatus(status)
            q = q.filter(OCRRecord.status == st)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if date_from:
        q = q.filter(OCRRecord.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        q = q.filter(
            OCRRecord.created_at < datetime.fromisoformat(date_to) + timedelta(days=1)
        )

    total = q.count()
    records = (
        q.order_by(OCRRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        items=[RecordOut(**r.to_dict()) for r in records],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/records/{record_id}", response_model=RecordOut)
def get_record(
    record_id: int,
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    r = db.query(OCRRecord).filter(OCRRecord.id == record_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return RecordOut(**r.to_dict())


@router.delete("/records/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    r = db.query(OCRRecord).filter(OCRRecord.id == record_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Record not found")

    # Delete associated files
    cfg = Config.from_env()
    img_path = cfg.upload_dir / r.image_filename
    if img_path.exists():
        img_path.unlink()
    if r.result_path:
        out_path = cfg.output_dir / Path(r.result_path).name
        if out_path.exists():
            out_path.unlink()

    db.delete(r)
    db.commit()
    return {"ok": True}


@router.post("/records/batch-delete")
def batch_delete(
    body: BatchDeleteRequest,
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    cfg = Config.from_env()
    records = db.query(OCRRecord).filter(OCRRecord.id.in_(body.ids)).all()

    for r in records:
        img_path = cfg.upload_dir / r.image_filename
        if img_path.exists():
            img_path.unlink()
        if r.result_path:
            out_path = cfg.output_dir / Path(r.result_path).name
            if out_path.exists():
                out_path.unlink()

    db.query(OCRRecord).filter(OCRRecord.id.in_(body.ids)).delete(
        synchronize_session=False
    )
    db.commit()
    return {"ok": True, "deleted": len(records)}


# ── Result content ───────────────────────────────────────────────────────────

@router.get("/results/{filename}")
def get_result_content(
    filename: str,
    _user: AdminUser = Depends(get_current_user),
):
    cfg = Config.from_env()
    path = cfg.output_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    return {"filename": filename, "content": path.read_text(encoding="utf-8")}


# ── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats/overview", response_model=StatsOverview)
def stats_overview(
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    row = db.query(
        func.count(OCRRecord.id).label("total"),
        func.sum(case((OCRRecord.status == RecordStatus.SUCCESS, 1), else_=0)).label("ok"),
        func.sum(case((OCRRecord.status == RecordStatus.FAILURE, 1), else_=0)).label("fail"),
        func.avg(OCRRecord.elapsed_ms).label("avg_ms"),
    ).first()

    return StatsOverview(
        total_calls=row.total or 0,
        success_count=row.ok or 0,
        failure_count=row.fail or 0,
        avg_elapsed_ms=round(row.avg_ms or 0, 1),
    )


@router.get("/stats/trend", response_model=list[TrendPoint])
def stats_trend(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(OCRRecord.created_at).label("d"),
            func.count(OCRRecord.id).label("c"),
        )
        .filter(OCRRecord.created_at >= since)
        .group_by("d")
        .order_by("d")
        .all()
    )
    return [TrendPoint(date=str(r.d), count=r.c) for r in rows]


@router.get("/stats/engines", response_model=list[EngineStat])
def stats_engines(
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    rows = (
        db.query(
            OCRRecord.engine,
            func.count(OCRRecord.id).label("c"),
        )
        .group_by(OCRRecord.engine)
        .all()
    )
    total = sum(r.c for r in rows) or 1
    return [
        EngineStat(engine=r.engine, count=r.c, pct=round(r.c / total * 100, 1))
        for r in rows
    ]


# ── Image list ───────────────────────────────────────────────────────────────

@router.get("/images")
def list_images(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user: AdminUser = Depends(get_current_user),
):
    cfg = Config.from_env()
    images = sorted(
        [p for p in cfg.upload_dir.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    total = len(images)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = images[start:end]

    return {
        "items": [
            {
                "filename": p.name,
                "size_bytes": p.stat().st_size,
                "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
            }
            for p in page_items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.delete("/images/{filename}")
def delete_image(
    filename: str,
    db: Session = Depends(get_session),
    _user: AdminUser = Depends(get_current_user),
):
    cfg = Config.from_env()
    path = cfg.upload_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404)

    path.unlink()
    # Also delete associated record and output
    record = db.query(OCRRecord).filter(OCRRecord.image_filename == filename).first()
    if record:
        out_path = cfg.output_dir / (Path(record.image_filename).stem + ".md")
        if out_path.exists():
            out_path.unlink()
        db.delete(record)
        db.commit()

    return {"ok": True}
