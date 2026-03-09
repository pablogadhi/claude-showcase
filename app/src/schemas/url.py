from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_code: str | None = Field(
        default=None,
        min_length=4,
        max_length=8,
        pattern=r"^[A-Za-z0-9]+$",
    )


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime


class URLInfoResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    click_count: int

    model_config = {"from_attributes": True}
