from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import models
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app. database import get_db
from app import auth, schemas, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)

) -> models.Users:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
