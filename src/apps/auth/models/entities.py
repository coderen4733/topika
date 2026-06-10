from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from src.core.config import REFRESH_TOKEN_EXPIRE


def get_current_utc() -> datetime:
    return datetime.now(UTC)


def get_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE)


class RefreshTokenEntity(BaseModel):
    user_id: str
    ip_address: str
    refresh_token: str = Field(..., json_schema_extra={"unique": True})

    created_at: datetime = Field(default_factory=get_current_utc)
    expires_at: datetime = Field(default_factory=get_expires_at)
