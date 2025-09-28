"""Authentication package for the quiz application."""

from .auth_state import AuthState
from .decorators import require_auth_component, require_teacher_component, require_student_component
from .middleware import auth_middleware

__all__ = ["AuthState", "require_auth_component", "require_teacher_component", "require_student_component", "auth_middleware"]
