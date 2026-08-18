from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db


router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db:Session =  Depends(get_db )):
    existing_book = crud.get_book_by_isbn(db, book.isbn)
    if existing_book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with this ISBN already exists.")
    return crud.create_book(db, book)


@router.get("/", response_model= List[schemas.BookResponse], status_code=status.HTTP_200_OK)
def read_books(skip: int = 0, limit:int = 10, db: Session = Depends(get_db) ):
    books = crud.get_books(db, skip,limit)
    return books

@router.get("/{book_id}", response_model=schemas.BookResponse, status_code=status.HTTP_200_OK)
def read_book(book_id:int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db,book_id)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book


@router.put("/{book_id}",response_model=schemas.BookResponse, status_code=status.HTTP_200_OK)
def update_book(book_id:int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)):
    db_book = crud.update_book(db, book_id, book_update)
    if db_book is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book

@router.delete("/{book_id}",response_model=schemas.BookResponse, status_code=status.HTTP_200_OK)
def delete_book(book_id:int, db: Session = Depends(get_db)):
    db_book = crud.delete_book(db, book_id)
    if db_book is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book






