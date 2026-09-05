from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/library_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema():
    """Create new tables and add authentication columns to existing users tables."""
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("users")
    }
    columns_to_add = {
        "username": "VARCHAR(50)",
        "hashed_password": "VARCHAR(255)",
        "role": "VARCHAR(20) DEFAULT 'member'",
        "is_verified": "BOOLEAN DEFAULT FALSE",
        "last_login": "TIMESTAMP WITH TIME ZONE",
        "updated_at": "TIMESTAMP WITH TIME ZONE",
    }

    missing_columns = {
        name: definition
        for name, definition in columns_to_add.items()
        if name not in existing_columns
    }
    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, definition in missing_columns.items():
            connection.execute(
                text(f'ALTER TABLE users ADD COLUMN "{name}" {definition}')
            )

        if "role" in missing_columns:
            connection.execute(
                text("UPDATE users SET role = 'member' WHERE role IS NULL")
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()