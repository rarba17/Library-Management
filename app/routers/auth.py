import email
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Any

from app.database import get_db
from app import auth, schemas, models,dependency

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

@router.post("/register", response_model=schemas.UserResponse,  status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
)-> Any:
    existing_user = db.query(models.Users).filter(
        models.Users.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    existing_email = db.query(models.Users).filter(
        models.Users.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    existing_name = db.query(models.Users).filter(
        models.Users.name == user_data.name
    ).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already exists"
        )

    # create new user
    hashed_password = auth.get_password_hash(user_data.password)
    db_user = models.Users(
        username = user_data.username,
        email = user_data.email,
        phone = user_data.phone,
        name = user_data.name,
        hashed_password = hashed_password,
        is_active = True,
        is_verified = False

    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    user = auth.authenticate_user(db,login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()


    tokens = auth.create_user_token(user, db)

    auth.store_refresh_token(db,user.id,tokens["refresh_token"])

    return tokens


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token"""
    user = auth.verify_refresh_token(db, refresh_request.refresh_token)

    # Create new tokens
    tokens = auth.create_user_token(user, db)

    # Store new refresh token
    auth.store_refresh_token(db, user.id, tokens["refresh_token"])

    return tokens

@router.post("/logout")
async def logout(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Logout user and revoke refresh token"""
    # Revoke the specific refresh token
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == refresh_request.refresh_token
    ).first()

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all_devices(
    current_user: models.Users = Depends(dependency.get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Logout from all devices by revoking all refresh tokens"""
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == current_user.id,
        models.RefreshToken.is_revoked == False
    ).update({"is_revoked": True})

    db.commit()
    return {"message": "Logged out from all devices successfully"}