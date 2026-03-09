from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import engine, Base
from src.routers import url as url_router
import src.models.url  # noqa: F401 — registers URL model with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="URL Shortener API",
    description="Shorten long URLs into compact links",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(url_router.router)
