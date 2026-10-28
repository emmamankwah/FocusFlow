"""Pydantic models for the authentication flow."""

import re
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def _strip(value):
    """Trim surrounding whitespace before any other validation runs."""
    return value.strip() if isinstance(value, str) else value


StrippedStr = Annotated[str, BeforeValidator(_strip)]

# Trim emails before validating them, so " user@example.com " and
# "user@example.com" reach the database and the lookups as the same value.
NormalizedEmail = Annotated[EmailStr, BeforeValidator(_strip)]


class PasswordValidation(BaseModel):
    @field_validator("password", "newPassword", check_fields=False)
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError(
                "Password must be at least 8 characters long."
            )
        if len(value) > 128:
            raise ValueError(
                "Password must be at most 128 characters long."
            )
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain an uppercase letter."
            )
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain a lowercase letter."
            )
        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain a number."
            )
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError(
                "Password must contain a special character."
            )
        return value


class UserLogin(BaseModel):
    email: NormalizedEmail = Field(max_length=255)
    password: str


class UserRegister(PasswordValidation):
    firstName: StrippedStr = Field(min_length=1, max_length=100)
    lastName: StrippedStr = Field(min_length=1, max_length=100)
    email: NormalizedEmail = Field(min_length=1, max_length=255)
    username: str 
    password: str
    confirmPassword: str 

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegister":
        if (
            self.confirmPassword is not None
            and self.password != self.confirmPassword
        ):
            raise ValueError("Passwords do not match.")
        return self


class ResetPassword(PasswordValidation):
    email: NormalizedEmail = Field(max_length=255)
    otp: StrippedStr = Field(min_length=1)
    newPassword: str


class ChangePassword(PasswordValidation):
    email: NormalizedEmail = Field(max_length=255)
    oldPassword: str
    newPassword: str


class OtpRequest(BaseModel):
    email: NormalizedEmail = Field(max_length=255)


class OtpVerification(BaseModel):
    email: NormalizedEmail = Field(max_length=255)
    otp: StrippedStr = Field(min_length=1)


class OtpResend(BaseModel):
    email: NormalizedEmail = Field(max_length=255)


class UserProfileUpdate(BaseModel):
    firstName: StrippedStr = Field(min_length=1, max_length=100)
    lastName: StrippedStr = Field(min_length=1, max_length=100)
    username: str
    email: NormalizedEmail = Field(max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    firstName: str
    lastName: str
    username: str
    email: NormalizedEmail
