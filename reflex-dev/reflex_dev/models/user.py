"""User model and role definitions."""

import enum
from typing import Optional
import reflex as rx
from sqlmodel import Field, SQLModel


class UserRole(enum.Enum):
    """User roles in the quiz application."""
    STUDENT = "student"
    TEACHER = "teacher"


class User(SQLModel, table=True):
    """Base user model for authentication."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True)  # student_id or teacher_id
    email: str = Field(unique=True, index=True)
    full_name: str
    role: UserRole
    password_hash: str
    is_active: bool = Field(default=True)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)
    
    class Config:
        """Configuration for the User model."""
        use_enum_values = True
