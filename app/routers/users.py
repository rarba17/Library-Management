from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from app import models, schemas, auth, dependency
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.Users = Depends(dependency.get_current_active_user)
) -> Any:
    """Get current user information"""
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_active_user)
) -> Any:
    """Update current user information"""
    update_data = user_update.model_dump(exclude_unset=True)

    # Don't allow role updates through this endpoint
    if "role" in update_data:
        del update_data["role"]

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password", response_model=dict)
async def update_password(
    password_update: schemas.UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_active_user)
) -> Any:
    """Update current user's password"""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not set for this account"
        )

    # Verify current password
    if not auth.verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = auth.get_password_hash(password_update.new_password)
    db.commit()

    return {"message": "Password updated successfully"}

@router.get("/", response_model=schemas.UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_admin_user)
) -> Any:
    """Get all users with pagination and search (Admin only)"""
    query = db.query(models.Users)

    # Apply search filter
    if search:
        query = query.filter(
            models.Users.username.ilike(f"%{search}%") |
            models.Users.email.ilike(f"%{search}%") |
            models.Users.name.ilike(f"%{search}%")
        )

    total = query.count()
    users = query.offset(skip).limit(limit).all()

    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_librarian_user)
) -> Any:
    """Get user by ID (Librarian+ only)"""
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can view their own profile, admins/librarians can view anyone
    if current_user.id != user_id and current_user.role not in [models.UserRole.ADMIN, models.UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_admin_user)
) -> Any:
    """Update user (Admin only)"""
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_admin_user)
) -> Any:
    """Delete user (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete - deactivate instead of hard delete
    user.is_active = False
    db.commit()

    return None

@router.post("/{user_id}/set-role", response_model=schemas.UserResponse)
async def set_user_role(
    user_id: int,
    role: models.UserRole,
    db: Session = Depends(get_db),
    current_user: models.Users = Depends(dependency.get_current_admin_user)
) -> Any:
    """Set user role (Admin only)"""
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    user.role = role
    db.commit()
    db.refresh(user)
    return user