from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, DateTime, Float, Text, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .database import Base
from typing import Optional, List
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    publisher = Column(String)
    year = Column(Integer)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    borrow_records = relationship("BorrowRecord", back_populates="book")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    borrower_name = Column(String, nullable=False)
    borrow_date = Column(DateTime(timezone=True), server_default=func.now())
    return_date = Column(DateTime(timezone=True), nullable=True)
    is_returned = Column(Boolean, default=False)

    book = relationship("Book", back_populates="borrow_records")
    user = relationship("Users", back_populates="borrow_records")

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    membership_date = Column(DateTime(timezone=True), server_default=func.now())

    # NEW: Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=True)  # Optional for backward compatibility
    hashed_password = Column(String(255), nullable=True)  # Nullable for existing users
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    borrow_records = relationship("BorrowRecord", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("Users", back_populates="refresh_tokens")