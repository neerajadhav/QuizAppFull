"""Authentication middleware."""

import reflex as rx
from reflex_dev.auth.auth_state import AuthState


def auth_middleware(request, response):
    """Authentication middleware to check user authentication status."""
    # This can be extended to handle session management,
    # token validation, etc.
    pass


def check_auth_status():
    """Check if user is authenticated and redirect if necessary."""
    state = AuthState()
    
    if not state.is_authenticated:
        return rx.redirect("/login")
    
    return None
