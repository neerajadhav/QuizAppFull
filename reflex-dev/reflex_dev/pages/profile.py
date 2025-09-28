"""Profile page for user information."""

import reflex as rx
from reflex_dev.components.layout import base_layout
from reflex_dev.components.cards import user_card
from reflex_dev.auth.auth_state import AuthState


def profile_page() -> rx.Component:
    """User profile page."""
    return base_layout(
        rx.container(
            rx.vstack(
                rx.heading("My Profile", size="6"),
                
                # User information card - simplified version
                rx.cond(
                    AuthState.is_authenticated,
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.avatar(
                                    fallback="U",
                                    size="6",
                                ),
                                rx.vstack(
                                    rx.heading(AuthState.user_display_name, size="4"),
                                    rx.text(AuthState.user_id_display, size="2", color=rx.color("gray", 10)),
                                    rx.badge(
                                        rx.cond(AuthState.is_teacher, "Teacher", "Student"),
                                        color_scheme=rx.cond(AuthState.is_teacher, "blue", "green"),
                                    ),
                                    spacing="1",
                                    align="start",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                            ),
                            spacing="4",
                            align="start",
                            width="100%",
                        ),
                        padding="4",
                        width="100%",
                    ),
                    rx.text("Please log in to view your profile."),
                ),
                
                # Edit profile button (placeholder for future functionality)
                rx.button(
                    "Edit Profile",
                    variant="outline",
                    size="3",
                    disabled=True,  # Will be enabled when edit functionality is added
                ),
                
                spacing="6",
                align="center",
                width="100%",
                max_width="600px",
            ),
            padding="6",
        )
    )
