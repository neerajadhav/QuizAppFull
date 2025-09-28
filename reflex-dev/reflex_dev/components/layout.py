"""Layout components for consistent page structure."""

import reflex as rx
from reflex_dev.components.navbar import navbar
from reflex_dev.auth.auth_state import AuthState


def base_layout(*children) -> rx.Component:
    """Base layout with navbar for all pages."""
    return rx.vstack(
        navbar(),
        rx.container(
            *children,
            max_width="1200px",
            padding="4",
            width="100%",
        ),
        spacing="0",
        width="100%",
        min_height="100vh",
    )


def dashboard_layout(title: str, *children) -> rx.Component:
    """Dashboard layout with sidebar navigation."""
    return base_layout(
        rx.hstack(
            # Sidebar
            rx.vstack(
                rx.heading(title, size="5"),
                rx.separator(),
                
                # Navigation based on role
                rx.cond(
                    AuthState.is_teacher,
                    # Teacher navigation
                    rx.vstack(
                        rx.link(
                            rx.button(
                                rx.icon("layout-dashboard", size=18),
                                "Dashboard",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/teacher/dashboard",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("file-plus", size=18),
                                "Create Quiz",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/teacher/quiz/create",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("list", size=18),
                                "My Quizzes",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/teacher/quizzes",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("users", size=18),
                                "Students",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/teacher/students",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    # Student navigation
                    rx.vstack(
                        rx.link(
                            rx.button(
                                rx.icon("layout-dashboard", size=18),
                                "Dashboard",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/student/dashboard",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("play", size=18),
                                "Available Quizzes",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/student/quizzes",
                        ),
                        rx.link(
                            rx.button(
                                rx.icon("bar-chart", size=18),
                                "My Results",
                                variant="ghost",
                                justify="start",
                                width="100%",
                            ),
                            href="/student/results",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                ),
                
                rx.spacer(),
                
                # User info at bottom
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.avatar(
                                fallback="U",
                                size="2",
                            ),
                            rx.vstack(
                                rx.text(AuthState.user_display_name, size="2", weight="medium"),
                                rx.text(AuthState.user_id_display, size="1", color=rx.color("gray", 10)),
                                spacing="0",
                                align="start",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    padding="2",
                    size="1",
                ),
                
                spacing="4",
                width="250px",
                min_height="calc(100vh - 100px)",
                padding="4",
                border_right="1px solid",
                border_color=rx.color("gray", 3),
            ),
            
            # Main content
            rx.vstack(
                *children,
                spacing="6",
                padding="6",
                width="100%",
                align="start",
            ),
            
            spacing="0",
            align="start",
            width="100%",
            min_height="calc(100vh - 100px)",
        )
    )


def auth_layout(*children) -> rx.Component:
    """Layout for authentication pages (login, register)."""
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.icon("graduation-cap", size=32),
                rx.heading("QuizApp", size="8"),
                spacing="3",
                align="center",
            ),
            *children,
            spacing="8",
            align="center",
            padding="6",
        ),
        min_height="100vh",
        background=rx.color("gray", 1),
    )
