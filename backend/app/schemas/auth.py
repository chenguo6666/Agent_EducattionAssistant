from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    phone: str
    password: str = Field(min_length=6, max_length=32)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("用户名不能为空")
        for char in normalized:
            is_valid = char.isalnum() or char == "_" or ("\u4e00" <= char <= "\u9fff")
            if not is_valid:
                raise ValueError("用户名仅支持中文、字母、数字和下划线")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) != 11 or not normalized.isdigit() or not normalized.startswith("1"):
            raise ValueError("手机号必须为 11 位数字")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 6:
            raise ValueError("密码长度不能少于 6 位")
        return normalized


class LoginRequest(BaseModel):
    account: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=32)

    @field_validator("account", "password")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("字段不能为空")
        return normalized


class UserResponse(BaseModel):
    id: int
    username: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
