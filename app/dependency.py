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

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = auth.decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception


    user = db.query(models.Users).filter(
        models.Users.username == token_data.sub,
        models.Users.is_active == True

    ).first()


    if not user:
        user = db.query(models.Users).filter(
            models.Users.email == token_data.sub,
            models.Users.is_active == True
        ).first()

    if user is None:
        raise credentials_exception


    return user


async def get_current_active_user(
        current_user: models.Users = Depends(get_current_user)
) -> models.Users:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
            )
    return current_user


async def get_current_admin_user(
        current_user: models.Users = Depends(get_current_active_user)

) -> models.Users:

    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have sufficient privileges"
        )
    return current_user


async def get_current_librarian_user(
        current_user: models.Users = Depends(get_current_active_user)

)-> models.Users:

    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have sufficient privileges"
        )
    return current_user

def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[models.Users]:
    """Get the current user if authenticated, otherwise return None"""
    if not token:
        return None

    try:
        payload = auth.decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None

        user = db.query(models.Users).filter(
            models.Users.username == username,
            models.Users.is_active == True
        ).first()

        if not user:
            user = db.query(models.Users).filter(
                models.Users.email == username,
                models.Users.is_active == True
            ).first()

        return user
    except:
        return None







