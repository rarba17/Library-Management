from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/",response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
  existing_user = crud.get_user_by_email(db, user.email)
  if existing_user:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists.")
  else:
    return crud.create_user(db=db, user=user)

@router.get("/",response_model=List[schemas.UserResponse])
def read_users(skip : int = 0, limit :int = 100 , db: Session = Depends(get_db)):
  users = crud.get_users(db=db, skip=skip, limit=limit)
  return users


@router.get("/{user_id}", response_model=schemas.UserResponse,status_code=status.HTTP_200_OK)
def read_user(user_id: int, db:Session = Depends(get_db)):
  user = crud.get_user(db,user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.put("/{user_id}",response_model=schemas.UserResponse,)
def update_user( user_id: int,user_update: schemas.UserUpdate,db: Session = Depends(get_db)):
  db_user = crud.update_user(db,user_id,user_update)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user


@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_user( user_id: int,db: Session = Depends(get_db)):
  db_user = crud.delete_user(db,user_id)
  if not db_user:
    raise HTTPException(status_code=404, detail="User not found")
  return db_user




