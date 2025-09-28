"""Card components for displaying information."""

import reflex as rx
from typing import Any, Dict


def user_card(user_data: Dict[str, Any]) -> rx.Component:
    """Create a user information card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.avatar(
                    fallback=user_data.get("full_name", "User")[0].upper(),
                    size="6",
                ),
                rx.vstack(
                    rx.heading(user_data.get("full_name", "Unknown User"), size="4"),
                    rx.text(
                        user_data.get("user_id", ""),
                        size="2",
                        color=rx.color("gray", 10),
                    ),
                    rx.badge(
                        user_data.get("role", "user").title(),
                        color_scheme="blue" if user_data.get("role") == "teacher" else "green",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            
            rx.separator(),
            
            # Additional info based on role
            rx.cond(
                user_data.get("role") == "teacher",
                rx.vstack(
                    rx.hstack(
                        rx.icon("building", size=16),
                        rx.text(f"Department: {user_data.get('department', 'N/A')}", size="2"),
                        spacing="2",
                    ),
                    rx.cond(
                        user_data.get("specialization"),
                        rx.hstack(
                            rx.icon("star", size=16),
                            rx.text(f"Specialization: {user_data.get('specialization')}", size="2"),
                            spacing="2",
                        ),
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.icon("book", size=16),
                        rx.text(f"Program: {user_data.get('program', 'N/A')}", size="2"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.icon("calendar", size=16),
                        rx.text(
                            f"Year {user_data.get('year_of_study', 'N/A')}, Semester {user_data.get('semester', 'N/A')}",
                            size="2"
                        ),
                        spacing="2",
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
            ),
            
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="4",
        width="100%",
    )


def stats_card(title: str, value: str, icon: str, color_scheme: str = "blue") -> rx.Component:
    """Create a statistics card."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, color=rx.color(color_scheme, 9)),
                rx.spacer(),
                justify="between",
                width="100%",
            ),
            rx.vstack(
                rx.heading(value, size="6", weight="bold"),
                rx.text(title, size="2", color=rx.color("gray", 10)),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="4",
        width="100%",
        min_height="120px",
    )


def quiz_card(quiz_data: Dict[str, Any]) -> rx.Component:
    """Create a quiz card for display."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(quiz_data.get("title", "Quiz"), size="4"),
                rx.spacer(),
                rx.badge(
                    quiz_data.get("status", "Active"),
                    color_scheme="green" if quiz_data.get("status") == "Active" else "gray",
                ),
                justify="between",
                width="100%",
            ),
            
            rx.text(
                quiz_data.get("description", "No description available"),
                size="2",
                color=rx.color("gray", 10),
            ),
            
            rx.hstack(
                rx.hstack(
                    rx.icon("clock", size=16),
                    rx.text(f"{quiz_data.get('duration', 60)} min", size="2"),
                    spacing="1",
                ),
                rx.hstack(
                    rx.icon("circle-help", size=16),
                    rx.text(f"{quiz_data.get('questions', 0)} questions", size="2"),
                    spacing="1",
                ),
                spacing="4",
            ),
            
            rx.button(
                "Take Quiz" if quiz_data.get("role") == "student" else "View Quiz",
                size="2",
                width="100%",
                variant="solid",
            ),
            
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="4",
        width="100%",
    )
