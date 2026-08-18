
from sqlalchemy import Integer,Column,String,Boolean,ForeignKey,DateTime,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

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

    borrow_records = relationship("BorrowRecord", back_populates="user")




