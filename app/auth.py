from ast import mod
from datetime import datetime, timedelta, timezone
from pyexpat import model
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from pydantic import deprecated
from sqlalchemy.orm import Session
from app import models, schemas
import os
from fastapi import Depends, HTTPException, status

from app import models, schemas
from app.database import get_db

SECRECT_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def verify_password(plain_password: str, hashed_pasword: str) -> bool:
    if len(plain_password.encode("utf-8")) > 72:
        return False
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_pasword.encode("ascii"),
    )

def get_password_hash(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be 72 bytes or fewer")
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("ascii")

def authenticate_user(db : Session , username: str, password: str) -> Optional[models.Users]:
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRECT_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data:dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRECT_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token=token, key=SECRECT_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"})


def create_user_token(user: models.Users, db : Session) -> Dict[str,str]:
    access_token = create_access_token(data = {"sub": user.username})

    refresh_token = create_refresh_token(data = {"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def store_refresh_token(db: Session, user_id : int, refresh_token: str) -> model.RefreshToken:
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.is_revoked == False
    ).update({"is_revoked": True})

    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_token = models.RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=expires_at
        )

    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token


def verify_refresh_token(db: Session, refresh_token: str) -> Optional[models.Users]:
    try:
        payload = decode_token(refresh_token)
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        db_token = db.query(models.RefreshToken).filter(
            models.RefreshToken.token == refresh_token,
            models.RefreshToken.is_revoked == False,
            models.RefreshToken.expires_at > datetime.now(datetime.timezone.utc)
        ).first()

        if db_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is revoked or expired"
            )
        user = db.query(model.Users).filter(models.Users.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
