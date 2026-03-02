from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database import get_db
from src.schemas.url import ShortenRequest, ShortenResponse, URLInfoResponse
from src.services import url as url_service
from src.config import settings


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.post("/api/v1/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(
    payload: ShortenRequest,
    db: AsyncSession = Depends(get_db),
):
    url_record = await url_service.create_short_url(
        db, str(payload.original_url), payload.custom_code
    )
    return ShortenResponse(
        short_code=url_record.short_code,
        short_url=f"{settings.base_url}/{url_record.short_code}",
        original_url=url_record.original_url,
        created_at=url_record.created_at,
    )


@router.get("/api/v1/info/{short_code}", response_model=URLInfoResponse)
async def get_url_info(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    url_record = await url_service.get_by_code(db, short_code)
    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return URLInfoResponse.model_validate(url_record)


@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    url_record = await url_service.get_and_increment(db, short_code)
    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=url_record.original_url, status_code=307)
