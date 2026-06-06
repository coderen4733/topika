from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# ObjectID를 문자열로 자동 변환해주는 타입 정의
PyObjectId = Annotated[
    str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)
]


# 회원가입(sign_up)
# 회원가입 요청 - Request Schema
class SignUpReq(BaseModel):
    # DB의 _id를 id로 불러오고, 결과값은 문자열로 변환
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str = Field(..., min_length=1, example="fastapi@gmail.com")
    nickname: str = Field(..., min_length=1, example="FastAPI")
    password: str = Field(..., min_length=1, example="Password12#$")

    model_config = ConfigDict(
        populate_by_name=True,  # 변수명(id)과 별칭(_id) 모두 허용
        arbitrary_types_allowed=True,  # ObjectId 같은 외부 타입 허용
        json_schema_extra={
            "example": {
                "email": "fastapi@gmail.com",
                "nickname": "FastAPI",
                "password": "Password12#$",
            }
        },
    )


# 회원가입 응답 - Response Schema
class SignUpRes(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    nickname: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "6a241da8d3ba388591b98cdd",
                "email": "fastapi@gmail.com",
                "nickname": "FastAPI",
            }
        },
    )


# 로그인(sign_in)
# 로그인 요청 - Request Schema
class SignInReq(BaseModel):
    email: str = Field(..., min_length=1, example="fastapi@gmail.com")
    password: str = Field(..., min_length=1, example="Password12#$")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "fastapi@gmail.com",
                "password": "Password12#$",
            }
        }
    )


# 로그인 응답 - Response Schema
class SignInRes(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# 액세스 토큰 재발급(re_token)
# 액세스 토큰 재발급 요청 - Request Schema
class ReTokenReq(BaseModel):
    refresh_token: str = Field(..., description="리프레시 토큰")


# 액세스 토큰 재발급 응답 - Response Schema
class ReTokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
