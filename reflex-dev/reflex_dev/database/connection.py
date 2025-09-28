"""Database connection and initialization."""

import os
from sqlmodel import create_engine, Session, SQLModel
from reflex_dev.models import User, Teacher, Student

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiz_app.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Initialize the database tables."""
    SQLModel.metadata.create_all(engine)


def get_db_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session
