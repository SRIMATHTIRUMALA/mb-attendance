from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserProfile"

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    role: Optional[str] = "employee"
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: str
    designation: str
    role: str
    joining_date: date
    is_active: bool
    phone: Optional[str] = None

    class Config:
        from_attributes = True

Token.model_rebuild()
