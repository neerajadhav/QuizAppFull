"""Authentication state management."""

from typing import Optional
import reflex as rx
from sqlmodel import Session
from reflex_dev.models import User, UserRole, Teacher, Student
from reflex_dev.database import get_db_session, UserCRUD, TeacherCRUD, StudentCRUD
from reflex_dev.database.connection import engine


class AuthState(rx.State):
    """Authentication state for the application."""
    
    # User authentication state
    is_authenticated: bool = False
    current_user: Optional[User] = None
    current_user_profile: Optional[dict] = None
    error_message: str = ""
    
    # Login form state
    login_user_id: str = ""
    login_password: str = ""
    
    # Registration form state
    register_user_id: str = ""
    register_email: str = ""
    register_full_name: str = ""
    register_password: str = ""
    register_confirm_password: str = ""
    register_role: str = "student"
    
    # Student-specific registration fields
    register_program: str = ""
    register_year_of_study: int = 1
    register_semester: int = 1
    
    # Teacher-specific registration fields
    register_department: str = ""
    register_specialization: str = ""
    
    # Setter methods (required for Reflex 0.8+)
    def set_login_user_id(self, value: str):
        self.login_user_id = value
    
    def set_login_password(self, value: str):
        self.login_password = value
    
    def set_register_user_id(self, value: str):
        self.register_user_id = value
    
    def set_register_email(self, value: str):
        self.register_email = value
    
    def set_register_full_name(self, value: str):
        self.register_full_name = value
    
    def set_register_password(self, value: str):
        self.register_password = value
    
    def set_register_confirm_password(self, value: str):
        self.register_confirm_password = value
    
    def set_register_role(self, value: str):
        self.register_role = value
    
    def set_register_program(self, value: str):
        self.register_program = value
    
    def set_register_year_of_study(self, value: str):
        self.register_year_of_study = int(value)
    
    def set_register_semester(self, value: str):
        self.register_semester = int(value)
    
    def set_register_department(self, value: str):
        self.register_department = value
    
    def set_register_specialization(self, value: str):
        self.register_specialization = value
    
    def login(self):
        """Handle user login."""
        if not self.login_user_id or not self.login_password:
            self.error_message = "Please enter both user ID and password"
            return
        
        try:
            with Session(engine) as session:
                user = UserCRUD.authenticate_user(
                    session, self.login_user_id, self.login_password
                )
                
                if user:
                    self.current_user = user
                    self.is_authenticated = True
                    self.error_message = ""
                    
                    # Update user flags and display info
                    self._update_user_flags()
                    
                    # Load user profile based on role
                    self._load_user_profile(session)
                    
                    # Redirect based on role
                    if user.role == UserRole.TEACHER:
                        return rx.redirect("/teacher/dashboard")
                    else:
                        return rx.redirect("/student/dashboard")
                else:
                    self.error_message = "Invalid user ID or password"
        except Exception as e:
            self.error_message = f"Login failed: {str(e)}"
    
    def logout(self):
        """Handle user logout."""
        self.is_authenticated = False
        self.current_user = None
        self.current_user_profile = None
        self.login_user_id = ""
        self.login_password = ""
        self.error_message = ""
        self._update_user_flags()
        return rx.redirect("/")
    
    def register(self):
        """Handle user registration."""
        if not self._validate_registration():
            return
        
        try:
            with Session(engine) as session:
                if self.register_role == "student":
                    student = StudentCRUD.create_student(
                        session=session,
                        student_id=self.register_user_id,
                        email=self.register_email,
                        full_name=self.register_full_name,
                        password=self.register_password,
                        program=self.register_program,
                        year_of_study=self.register_year_of_study,
                        semester=self.register_semester
                    )
                    self.error_message = "Student registration successful! Please login."
                else:
                    teacher = TeacherCRUD.create_teacher(
                        session=session,
                        teacher_id=self.register_user_id,
                        email=self.register_email,
                        full_name=self.register_full_name,
                        password=self.register_password,
                        department=self.register_department,
                        specialization=self.register_specialization
                    )
                    self.error_message = "Teacher registration successful! Please login."
                
                # Clear form
                self._clear_registration_form()
                
        except Exception as e:
            self.error_message = f"Registration failed: {str(e)}"
    
    def _validate_registration(self) -> bool:
        """Validate registration form."""
        if not all([
            self.register_user_id,
            self.register_email,
            self.register_full_name,
            self.register_password,
            self.register_confirm_password
        ]):
            self.error_message = "Please fill in all required fields"
            return False
        
        if self.register_password != self.register_confirm_password:
            self.error_message = "Passwords do not match"
            return False
        
        if len(self.register_password) < 6:
            self.error_message = "Password must be at least 6 characters long"
            return False
        
        if self.register_role == "student" and not self.register_program:
            self.error_message = "Please enter your program"
            return False
        
        if self.register_role == "teacher" and not self.register_department:
            self.error_message = "Please enter your department"
            return False
        
        return True
    
    def _clear_registration_form(self):
        """Clear registration form."""
        self.register_user_id = ""
        self.register_email = ""
        self.register_full_name = ""
        self.register_password = ""
        self.register_confirm_password = ""
        self.register_program = ""
        self.register_department = ""
        self.register_specialization = ""
    
    def _load_user_profile(self, session):
        """Load user profile based on role."""
        if not self.current_user:
            return
        
        if self.current_user.role == UserRole.TEACHER:
            teacher = TeacherCRUD.get_teacher_by_id(session, self.current_user.user_id)
            if teacher:
                self.current_user_profile = {
                    "type": "teacher",
                    "teacher_id": teacher.teacher_id,
                    "department": teacher.department,
                    "specialization": teacher.specialization,
                    "contact_number": teacher.contact_number,
                    "office_location": teacher.office_location,
                }
        else:
            student = StudentCRUD.get_student_by_id(session, self.current_user.user_id)
            if student:
                self.current_user_profile = {
                    "type": "student",
                    "student_id": student.student_id,
                    "program": student.program,
                    "year_of_study": student.year_of_study,
                    "semester": student.semester,
                    "gpa": student.gpa,
                }
    
    # Simple boolean properties instead of complex rx.var
    is_teacher: bool = False
    is_student: bool = False
    user_display_name: str = ""
    user_id_display: str = ""
    
    def _update_user_flags(self):
        """Update user flags and display information."""
        if self.is_authenticated and self.current_user:
            self.is_teacher = self.current_user.role == UserRole.TEACHER
            self.is_student = self.current_user.role == UserRole.STUDENT
            self.user_display_name = self.current_user.full_name
            self.user_id_display = self.current_user.user_id
        else:
            self.is_teacher = False
            self.is_student = False
            self.user_display_name = ""
            self.user_id_display = ""
