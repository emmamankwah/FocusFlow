from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str

class OtpRequest(BaseModel):
    email: EmailStr


class OtpVerification(BaseModel):
    email: EmailStr
    otp: str

class OtpResend(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr

