from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# User Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    role: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)

class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

    @model_validator(mode='after')
    def validate_unique_fields(self) -> 'UserCreate':
        # You can add cross-field validation here if needed
        # For example, ensure username is not the same as email
        if self.username.lower() == self.email.split('@')[0].lower():
            raise ValueError('Username cannot be the same as email prefix')
        return self

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, v))
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError('Phone number must be between 10 and 15 digits')
            return cleaned
        return v

class UserPasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserPasswordUpdate':
        if self.current_password == self.new_password:
            raise ValueError('New password must be different from current password')
        return self

class UserResponse(UserBase):
    id: int
    username: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    membership_date: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

# Login Schemas
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

# Book Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=20)
    publisher: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    total_copies: int = Field(1, ge=1)

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        # Remove hyphens and spaces
        cleaned = v.replace('-', '').replace(' ', '')
        if len(cleaned) not in [10, 13]:
            raise ValueError('ISBN must be 10 or 13 digits long')
        return cleaned

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    publisher: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    total_copies: Optional[int] = Field(None, ge=1)
    available_copies: Optional[int] = Field(None, ge=0)

    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.replace('-', '').replace(' ', '')
            if len(cleaned) not in [10, 13]:
                raise ValueError('ISBN must be 10 or 13 digits long')
            return cleaned
        return v

    @model_validator(mode='after')
    def validate_copies(self) -> 'BookUpdate':
        if self.total_copies is not None and self.available_copies is not None:
            if self.available_copies > self.total_copies:
                raise ValueError('Available copies cannot exceed total copies')
        return self

class BookResponse(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Borrow Record Schemas
class BorrowRecordBase(BaseModel):
    book_id: int = Field(..., gt=0)
    borrower_name: str = Field(..., min_length=1, max_length=255)
    borrow_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    is_returned: bool = False

class BorrowRecordCreate(BaseModel):
    book_id: int = Field(..., gt=0)
    borrower_name: str = Field(..., min_length=1, max_length=255)
    user_id: Optional[int] = Field(None, gt=0)

    @model_validator(mode='after')
    def validate_borrower(self) -> 'BorrowRecordCreate':
        # If user_id is provided, we could fetch the user's name
        # This is just a validation example
        if self.user_id is None and not self.borrower_name:
            raise ValueError('Either user_id or borrower_name must be provided')
        return self

class BorrowRecordResponse(BorrowRecordBase):
    id: int
    user_id: Optional[int] = None
    borrow_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool

    model_config = ConfigDict(from_attributes=True)

class BorrowRecordUpdate(BaseModel):
    return_date: Optional[datetime] = None
    is_returned: Optional[bool] = None

    @model_validator(mode='after')
    def validate_return(self) -> 'BorrowRecordUpdate':
        if self.is_returned is True and self.return_date is None:
            # If marking as returned, set return_date to now if not provided
            # This can be handled in the service layer instead
            pass
        return self

# Additional Schemas for Agent Integration (Future)
class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = Field(5, ge=1, le=20)
    include_borrowed: bool = False
    genre_preferences: Optional[List[str]] = None

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[BookResponse]
    confidence_scores: Optional[List[float]] = None
    reasoning: Optional[List[str]] = None
    generated_at: datetime = Field(default_factory=datetime.now)

class InventoryAlert(BaseModel):
    book_id: int
    title: str
    current_copies: int
    threshold: int
    alert_type: str  # "low_stock", "out_of_stock", "overstock"
    severity: str  # "info", "warning", "critical"
    timestamp: datetime = Field(default_factory=datetime.now)
    suggested_action: Optional[str] = None

class UserActivity(BaseModel):
    user_id: int
    action_type: str  # "borrow", "return", "search", "view"
    book_id: Optional[int] = None
    search_query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = None

# Pydantic Settings for configuration (optional)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    database_url: str = Field(..., env="DATABASE_URL")

    # Agent configuration
    enable_recommendations: bool = Field(True, env="ENABLE_RECOMMENDATIONS")
    enable_inventory_alert: bool = Field(True, env="ENABLE_INVENTORY_ALERT")
    ai_model_provider: str = Field("openai", env="AI_MODEL_PROVIDER")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")