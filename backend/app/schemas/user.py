from typing import Optional
import unicodedata

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# This schema defines what a frontend must send when creating a new account.
# It validates the request body before the user is saved to the database.
class UserCreate(BaseModel):
    # Keep required names within the 100-character database column limit.
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    # Used to catch password-entry mistakes during registration; checked below.
    confirm_password: str = Field(min_length=8, max_length=100) 
    # User's preferred timezone; default to UTC when none is provided.
    timezone: str = "UTC"

    # Allow Unicode letters, combining marks, spaces, and common name punctuation.
    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def validate_name_characters(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        value = value.strip()
        has_letter = False
        allowed_punctuation = " '-.\u2019\u2010\u2011\u2012\u2013\u2014"

        for character in value:
            category = unicodedata.category(character)
            if category.startswith("L"):
                has_letter = True
            elif category.startswith("M") or character in allowed_punctuation:
                continue
            else:
                raise ValueError(
                    "Names may contain letters, spaces, apostrophes, hyphens, and periods only"
                )

        if not has_letter:
            raise ValueError("Names must contain at least one letter")

        return value[0].upper() + value[1:]

    @model_validator(mode="after")
    def passwords_match(self):
        """Ensure the password and confirmation match before saving the user."""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
    


# This schema defines the expected request body for the login endpoint.
# The frontend sends an email and password to receive a JWT token.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# This is the response shape returned after a successful login.
# It contains the JWT access token and the type of token used.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# This schema is used to carry token-related claims such as the user email.
# It is helpful when decoding token payloads or representing auth session details.
class TokenData(BaseModel):
    email: Optional[str] = None

# Request body for verifying an account's email address with its emailed OTP.
class VerifyEmailRequest(BaseModel):
    # Identifies the account whose email address is being verified.
    email: EmailStr
    # Keep the OTP as text so codes with leading zeroes remain intact.
    otp: str = Field(pattern=r"^[0-9]{6}$")


class ResendOtpRequest(BaseModel):
    email: EmailStr


# This schema defines how user data is returned to the client after registration or profile fetch.
# It hides sensitive fields like the password hash and exposes only safe public info.
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    # Indicates whether the account's email verification has been completed.
    is_verified: bool

    class Config:
        from_attributes = True