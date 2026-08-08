from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

from app.models import Base

# for books

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: Optional[str] = None
    year: Optional[int] = None
    total_copies: Optional[int] = 1

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None

class Bookresponse(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# for borrow records

class BorrowRecordBase(BaseModel):
    book_id: int
    borrower_name: str
    borrow_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    is_returned: Optional[bool] = False

class BorrowRecordCreate(BorrowRecordBase):
    pass

class BorrowRecordResponse(BorrowRecordBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    status: str


    class Config:
        from_attributes = True

# for users

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    membership_date: datetime

    class Config:
        from_attributes = True





