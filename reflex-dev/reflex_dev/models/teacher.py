"""Teacher model extending the base User model."""

from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .user import User, UserRole


class Teacher(SQLModel, table=True):
    """Teacher-specific model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: str = Field(unique=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    department: str
    specialization: Optional[str] = None
    contact_number: Optional[str] = None
    office_location: Optional[str] = None
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
    
    # Relationship with User
    user: Optional[User] = Relationship()
    
    def __str__(self) -> str:
        return f"Teacher({self.teacher_id})"
