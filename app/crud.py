from turtle import title

from anyio import value
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime
from typing import List, Optional

def get_book(db: Session, book_id:int)->Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_book_by_isbn(db:Session, isbn: str)-> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def get_books(db: Session, skip: int = 0, limit: int=100)-> List[models.Book]:
    return db.query(models.Book).offset(skip).limit(limit).all()


def create_book(db: Session, book: schemas.BookCreate)-> models.Book:
    db_book = models.Book(
        title=book.title,
        author = book.author,
        isbn = book.isbn,
        publisher = book.publisher,
        year = book.year,
        total_copies = book.total_copies,
        available_copies = book.total_copies,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookUpdate)-> Optional[models.Book]:
    db_book = get_book(db, book_id)

    if db_book:
        update_data = book_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_book, key, value)

        db.commit()
        db.refresh(db_book)
        return db_book
def delete_book(db:Session, book_id:int)-> Optional[models.Book]:
    db_book = get_book(db,book_id)
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book


def get_user(db: Session, user_id: int) -> Optional[models.Users]:
    return db.query(models.Users).filter(models.Users.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.Users]:
    return db.query(models.Users).filter(models.Users.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Users]:
    return db.query(models.Users).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.Users:
    db_user = models.Users(
        name=user.name,
        email=user.email,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.Users]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[models.Users]:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# Borrow Record CRUD
def borrow_book(db: Session, borrow_data: schemas.BorrowRecordCreate) -> Optional[models.BorrowRecord]:
    book = get_book(db, borrow_data.book_id)
    if not book or book.available_copies <= 0:
        return None

    db_borrow = models.BorrowRecord(
        book_id=borrow_data.book_id,
        borrower_name=borrow_data.borrower_name,
        is_returned=False
    )

    book.available_copies -= 1

    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def return_book(db: Session, borrow_id: int) -> Optional[models.BorrowRecord]:
    db_borrow = db.query(models.BorrowRecord).filter(
        models.BorrowRecord.id == borrow_id,
        models.BorrowRecord.is_returned == False
    ).first()

    if not db_borrow:
        return None

    db_borrow.return_date = datetime.now()
    db_borrow.is_returned = True

    book = get_book(db, db_borrow.book_id)
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def get_borrow_records(db: Session, skip: int = 0, limit: int = 100) -> List[models.BorrowRecord]:
    return db.query(models.BorrowRecord).offset(skip).limit(limit).all()

def get_user_borrow_records(db: Session, user_id: int) -> List[models.BorrowRecord]:
    return db.query(models.BorrowRecord).filter(
        models.BorrowRecord.user_id == user_id
    ).all()



