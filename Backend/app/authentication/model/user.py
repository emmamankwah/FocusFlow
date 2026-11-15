"""Pydantic models for the authentication flow."""

import re
from typing import Annotated

from email_validator import EmailNotValidError, validate_email
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


def _strip(value):
    """Trim surrounding whitespace before any other validation runs."""
    return value.strip() if isinstance(value, str) else value


StrippedStr = Annotated[str, BeforeValidator(_strip)]


def _strip_and_validate_email(value):
    """Trim surrounding whitespace and validate without changing the casing."""
    if not isinstance(value, str):
        return value
    value = value.strip()
    try:
        validate_email(value, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc
    return value


# Email casing is part of the account identity: only surrounding whitespace is
# removed, and the validated value is stored exactly as entered.
TrimmedEmail = Annotated[str, BeforeValidator(_strip_and_validate_email)]


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
    email: TrimmedEmail = Field(max_length=255)
    password: str


class UserRegister(PasswordValidation):
    firstName: StrippedStr = Field(min_length=1, max_length=100)
    lastName: StrippedStr = Field(min_length=1, max_length=100)
    email: TrimmedEmail = Field(min_length=1, max_length=255)
    username: StrippedStr = Field(
        min_length=1,
        max_length=100,
        pattern=r"^\S+$",
    )
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
    email: TrimmedEmail = Field(min_length=1, max_length=255)
    otp: StrippedStr = Field(min_length=1)
    newPassword: str


class ChangePassword(PasswordValidation):
    model_config = ConfigDict(extra="forbid")

    oldPassword: str
    newPassword: str


class OtpRequest(BaseModel):
    email: TrimmedEmail = Field(min_length=1, max_length=255)


class OtpVerification(BaseModel):
    email: TrimmedEmail = Field(min_length=1, max_length=255)
    otp: StrippedStr = Field(min_length=1)


class OtpResend(BaseModel):
    email: TrimmedEmail = Field(min_length=1, max_length=255)


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    firstName: StrippedStr = Field(min_length=1, max_length=100)
    lastName: StrippedStr = Field(min_length=1, max_length=100)
    username: StrippedStr = Field(
        min_length=1,
        max_length=100,
        pattern=r"^\S+$",
    )


class EmailChangeRequest(BaseModel):
    newEmail: TrimmedEmail = Field(min_length=1, max_length=255)
    currentPassword: str = Field(min_length=1)


class EmailChangeVerification(BaseModel):
    otp: StrippedStr = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    firstName: str
    lastName: str
    username: str
    email: str
