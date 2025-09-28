"""CRUD operations for database models."""

from typing import Optional, List
from sqlmodel import Session, select
from reflex_dev.models import User, Teacher, Student, UserRole
from reflex_dev.utils.security import hash_password, verify_password


class UserCRUD:
    """CRUD operations for User model."""
    
    @staticmethod
    def create_user(
        session: Session,
        user_id: str,
        email: str,
        full_name: str,
        role: UserRole,
        password: str
    ) -> User:
        """Create a new user."""
        password_hash = hash_password(password)
        user = User(
            user_id=user_id,
            email=email,
            full_name=full_name,
            role=role,
            password_hash=password_hash
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: str) -> Optional[User]:
        """Get user by user_id (student_id or teacher_id)."""
        statement = select(User).where(User.user_id == user_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def authenticate_user(session: Session, user_id: str, password: str) -> Optional[User]:
        """Authenticate user with user_id and password."""
        user = UserCRUD.get_user_by_id(session, user_id)
        if user and verify_password(password, user.password_hash):
            return user
        return None
    
    @staticmethod
    def update_user(session: Session, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        user = UserCRUD.get_user_by_id(session, user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    
    @staticmethod
    def get_all_users(session: Session) -> List[User]:
        """Get all users."""
        statement = select(User)
        return list(session.exec(statement).all())


class TeacherCRUD:
    """CRUD operations for Teacher model."""
    
    @staticmethod
    def create_teacher(
        session: Session,
        teacher_id: str,
        email: str,
        full_name: str,
        password: str,
        department: str,
        **kwargs
    ) -> Teacher:
        """Create a new teacher with associated user."""
        # Create user first
        user = UserCRUD.create_user(
            session, teacher_id, email, full_name, UserRole.TEACHER, password
        )
        
        # Create teacher profile
        teacher = Teacher(
            teacher_id=teacher_id,
            user_id=user.id,
            department=department,
            **kwargs
        )
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return teacher
    
    @staticmethod
    def get_teacher_by_id(session: Session, teacher_id: str) -> Optional[Teacher]:
        """Get teacher by teacher_id."""
        statement = select(Teacher).where(Teacher.teacher_id == teacher_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all_teachers(session: Session) -> List[Teacher]:
        """Get all teachers."""
        statement = select(Teacher)
        return list(session.exec(statement).all())


class StudentCRUD:
    """CRUD operations for Student model."""
    
    @staticmethod
    def create_student(
        session: Session,
        student_id: str,
        email: str,
        full_name: str,
        password: str,
        program: str,
        year_of_study: int,
        semester: int,
        **kwargs
    ) -> Student:
        """Create a new student with associated user."""
        # Create user first
        user = UserCRUD.create_user(
            session, student_id, email, full_name, UserRole.STUDENT, password
        )
        
        # Create student profile
        student = Student(
            student_id=student_id,
            user_id=user.id,
            program=program,
            year_of_study=year_of_study,
            semester=semester,
            **kwargs
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        return student
    
    @staticmethod
    def get_student_by_id(session: Session, student_id: str) -> Optional[Student]:
        """Get student by student_id."""
        statement = select(Student).where(Student.student_id == student_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all_students(session: Session) -> List[Student]:
        """Get all students."""
        statement = select(Student)
        return list(session.exec(statement).all())
