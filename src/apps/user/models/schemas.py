from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.apps.auth.models.schemas import (
    PyObjectId,  # 기존에 만든 PyObjectId 가져오기
)


class UserMeRes(BaseModel):
    id: PyObjectId = Field(alias="_id")

    email: EmailStr
    nickname: str

    role: str

    sign_in_type: str

    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True
    )
