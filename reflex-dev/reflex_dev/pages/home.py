"""Home page component."""

import reflex as rx
from reflex_dev.components.layout import base_layout
from reflex_dev.auth.auth_state import AuthState


def home_page() -> rx.Component:
    """Home page with welcome content."""
    return base_layout(
        rx.center(
            rx.vstack(
                # Hero section
                rx.vstack(
                    rx.icon("graduation-cap", size=64, color=rx.color("blue", 9)),
                    rx.heading("Welcome to QuizApp", size="9", text_align="center"),
                    rx.text(
                        "A comprehensive quiz platform for teachers and students",
                        size="5",
                        text_align="center",
                        color=rx.color("gray", 10),
                    ),
                    spacing="4",
                    align="center",
                ),
                
                # Features section
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.icon("users", size=32, color=rx.color("blue", 9)),
                            rx.heading("Role-Based Access", size="4"),
                            rx.text(
                                "Separate interfaces for teachers and students with appropriate permissions",
                                size="2",
                                text_align="center",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding="6",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.icon("clipboard-list", size=32, color=rx.color("green", 9)),
                            rx.heading("Easy Quiz Creation", size="4"),
                            rx.text(
                                "Teachers can create and manage quizzes with various question types",
                                size="2",
                                text_align="center",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding="6",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.icon("bar-chart", size=32, color=rx.color("purple", 9)),
                            rx.heading("Performance Analytics", size="4"),
                            rx.text(
                                "Track student progress and quiz performance with detailed analytics",
                                size="2",
                                text_align="center",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding="6",
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                
                # CTA section
                rx.cond(
                    AuthState.is_authenticated,
                    # Authenticated user - show dashboard link
                    rx.vstack(
                        rx.text("Welcome back!", size="4", weight="medium"),
                        rx.link(
                            rx.button(
                                "Go to Dashboard",
                                size="4",
                                variant="solid",
                            ),
                            href=rx.cond(
                                AuthState.is_teacher,
                                "/teacher/dashboard",
                                "/student/dashboard"
                            ),
                        ),
                        spacing="3",
                        align="center",
                    ),
                    # Non-authenticated user - show auth buttons
                    rx.vstack(
                        rx.text("Get started today!", size="4", weight="medium"),
                        rx.hstack(
                            rx.link(
                                rx.button("Login", size="4", variant="outline"),
                                href="/login",
                            ),
                            rx.link(
                                rx.button("Register", size="4", variant="solid"),
                                href="/register",
                            ),
                            spacing="3",
                        ),
                        spacing="3",
                        align="center",
                    ),
                ),
                
                spacing="9",
                align="center",
                max_width="1000px",
                padding="6",
            ),
            width="100%",
            min_height="80vh",
        )
    )
