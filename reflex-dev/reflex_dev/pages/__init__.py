"""Page components for the quiz application."""

from .auth import login_page, register_page
from .dashboard import teacher_dashboard, student_dashboard
from .home import home_page
from .profile import profile_page

__all__ = ["login_page", "register_page", "teacher_dashboard", "student_dashboard", "home_page", "profile_page"]
