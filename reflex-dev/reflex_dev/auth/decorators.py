"""Authentication utilities for components."""

import reflex as rx
from reflex_dev.auth.auth_state import AuthState


def require_auth_component(content: rx.Component) -> rx.Component:
    """Wrap a component to require authentication."""
    return rx.cond(
        AuthState.is_authenticated,
        content,
        rx.center(
            rx.vstack(
                rx.heading("Authentication Required", size="6"),
                rx.text("Please log in to access this page."),
                rx.link(
                    rx.button("Login"),
                    href="/login",
                ),
                spacing="4",
                align="center",
            ),
            min_height="80vh",
        ),
    )


def require_teacher_component(content: rx.Component) -> rx.Component:
    """Wrap a component to require teacher role."""
    return rx.cond(
        AuthState.is_authenticated,
        rx.cond(
            AuthState.is_teacher,
            content,
            rx.center(
                rx.vstack(
                    rx.heading("Teacher Access Required", size="6"),
                    rx.text("This page is only accessible to teachers."),
                    rx.link(
                        rx.button("Back to Home"),
                        href="/",
                    ),
                    spacing="4",
                    align="center",
                ),
                min_height="80vh",
            ),
        ),
        rx.center(
            rx.vstack(
                rx.heading("Authentication Required", size="6"),
                rx.text("Please log in to access this page."),
                rx.link(
                    rx.button("Login"),
                    href="/login",
                ),
                spacing="4",
                align="center",
            ),
            min_height="80vh",
        ),
    )


def require_student_component(content: rx.Component) -> rx.Component:
    """Wrap a component to require student role."""
    return rx.cond(
        AuthState.is_authenticated,
        rx.cond(
            AuthState.is_student,
            content,
            rx.center(
                rx.vstack(
                    rx.heading("Student Access Required", size="6"),
                    rx.text("This page is only accessible to students."),
                    rx.link(
                        rx.button("Back to Home"),
                        href="/",
                    ),
                    spacing="4",
                    align="center",
                ),
                min_height="80vh",
            ),
        ),
        rx.center(
            rx.vstack(
                rx.heading("Authentication Required", size="6"),
                rx.text("Please log in to access this page."),
                rx.link(
                    rx.button("Login"),
                    href="/login",  
                ),
                spacing="4",
                align="center",
            ),
            min_height="80vh",
        ),
    )
