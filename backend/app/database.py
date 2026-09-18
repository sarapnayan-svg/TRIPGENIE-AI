"""
TripGenie AI — Database Connection & Session Management.
Supports PostgreSQL (via psycopg) with transparent fallback to local persistent SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL from environment or standard PostgreSQL default
DEFAULT_PG_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/tripgenie"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_PG_URL).strip()

FALLBACK_SQLITE_URL = "sqlite:///./tripgenie.db"

# Engine initialization with automatic resilience
engine = None
try:
    if DATABASE_URL.startswith("postgresql"):
        # Test PostgreSQL connection quickly with short connect_timeout
        temp_engine = create_engine(
            DATABASE_URL,
            connect_args={"connect_timeout": 2},
            pool_pre_ping=True,
        )
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
        print(f"[DATABASE] Connected to PostgreSQL successfully at: {DATABASE_URL.split('@')[-1]}")
    else:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
except Exception as e:
    print(f"[DATABASE NOTICE] PostgreSQL unreachable ({e}). Using persistent local SQLite fallback: {FALLBACK_SQLITE_URL}")
    engine = create_engine(
        FALLBACK_SQLITE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    from app import db_models  # Ensure models are imported
    Base.metadata.create_all(bind=engine)
