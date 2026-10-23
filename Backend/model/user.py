
import re

from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    model_validator,
)


class PasswordValidation(BaseModel):
    @field_validator("password", "new_password", check_fields=False)
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError(
                "Password must be at least 8 characters long."
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


class UserLogin(PasswordValidation):
    email: EmailStr
    username: str
    password: str


class UserRegister(PasswordValidation):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class ResetPassword(PasswordValidation):
    email: EmailStr
    otp: str
    new_password: str


class ChangePassword(PasswordValidation):
    email: EmailStr
    old_password: str
    new_password: str


class OtpRequest(BaseModel):
    email: EmailStr


class OtpVerification(BaseModel):
    email: EmailStr
    otp: str


class OtpResend(BaseModel):
    email: EmailStr


class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
