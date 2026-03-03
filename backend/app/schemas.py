from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role: str = "employee"


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class QuestionCreate(BaseModel):
    text: str


class QuestionOut(BaseModel):
    id: int
    question_text: str
    answer_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: int
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(DocumentOut):
    content: str

