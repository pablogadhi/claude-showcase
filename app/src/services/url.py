import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.models.url import URL


ALPHABET = string.ascii_letters + string.digits
MAX_RETRIES = 5


def generate_short_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


async def create_short_url(
    session: AsyncSession,
    original_url: str,
    custom_code: str | None = None,
) -> URL:
    for attempt in range(MAX_RETRIES):
        if custom_code and attempt == 0:
            code = custom_code
        else:
            code = generate_short_code(length=8 if attempt >= MAX_RETRIES - 2 else 6)
        try:
            record = URL(short_code=code, original_url=original_url)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record
        except IntegrityError:
            await session.rollback()
            if custom_code and attempt == 0:
                raise HTTPException(status_code=409, detail="Custom code already taken")
    raise HTTPException(status_code=500, detail="Could not generate a unique short code")


async def get_by_code(session: AsyncSession, short_code: str) -> URL | None:
    result = await session.execute(
        select(URL).where(URL.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def get_and_increment(session: AsyncSession, short_code: str) -> URL | None:
    result = await session.execute(
        update(URL)
        .where(URL.short_code == short_code)
        .values(click_count=URL.click_count + 1)
        .returning(URL)
    )
    await session.commit()
    return result.scalar_one_or_none()
