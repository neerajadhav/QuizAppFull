"""Student model extending the base User model."""

from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from .user import User, UserRole


class Student(SQLModel, table=True):
    """Student-specific model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(unique=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    program: str  # e.g., "Computer Science", "Mathematics"
    year_of_study: int  # 1, 2, 3, 4 for undergraduate
    semester: int  # current semester
    gpa: Optional[float] = None
    enrollment_date: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    
    # Relationship with User
    user: Optional[User] = Relationship()
    
    def __str__(self) -> str:
        return f"Student({self.student_id})"
