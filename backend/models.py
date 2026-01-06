from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class SignupRequest(BaseModel):
    email: str
    password: str

class ConfirmSignupRequest(BaseModel):
    email: str
    otp: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ConfirmForgotPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

class _ProfileBase(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    height: Optional[int] = Field(None, ge=50, le=300)
    gender: Optional[str]
    dob: Optional[date]

    @validator("gender")
    def validate_gender(cls, value):
        if value is None:
            return value

        allowed = {"male", "female", "other"}
        if value.lower() not in allowed:
            raise ValueError("gender must be male, female, or other")
        return value.lower()


class ProfileCreate(_ProfileBase):
    name: str
    height: int
    gender: str
    dob: date


class ProfileUpdate(_ProfileBase):
    pass


class ProfileResponse(_ProfileBase):
    user_id: str
    email: str
    profile_image_key: Optional[str]
