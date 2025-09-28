"""Navigation bar component."""

import reflex as rx
from reflex_dev.auth.auth_state import AuthState


def navbar() -> rx.Component:
    """Create a responsive navigation bar."""
    return rx.box(
        rx.hstack(
            # Logo/Brand
            rx.link(
                rx.hstack(
                    rx.icon("graduation-cap", size=24),
                    rx.text("QuizApp", size="6", weight="bold"),
                    spacing="2",
                ),
                href="/",
                _hover={"text_decoration": "none"},
            ),
            
            # Navigation Links
            rx.spacer(),
            
            # Conditional rendering based on auth state
            rx.cond(
                AuthState.is_authenticated,
                # Authenticated user menu
                rx.hstack(
                    rx.text(f"Welcome, {AuthState.user_display_name}"),
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.button(
                                rx.icon("user"),
                                AuthState.user_id_display,
                                variant="ghost",
                            )
                        ),
                        rx.menu.content(
                            rx.cond(
                                AuthState.is_teacher,
                                rx.menu.item(
                                    rx.link("Dashboard", href="/teacher/dashboard"),
                                ),
                                rx.menu.item(
                                    rx.link("Dashboard", href="/student/dashboard"),
                                ),
                            ),
                            rx.menu.item(
                                rx.link("Profile", href="/profile"),
                            ),
                            rx.menu.separator(),
                            rx.menu.item(
                                rx.button(
                                    "Logout",
                                    on_click=AuthState.logout,
                                    variant="ghost",
                                    color_scheme="red",
                                ),
                            ),
                        ),
                    ),
                    spacing="4",
                ),
                # Non-authenticated user menu
                rx.hstack(
                    rx.link(
                        rx.button("Login", variant="ghost"),
                        href="/login",
                    ),
                    rx.link(
                        rx.button("Register", variant="solid"),
                        href="/register",
                    ),
                    spacing="2",
                ),
            ),
            
            # Theme toggle
            rx.color_mode.button(),
            
            justify="between",
            align="center",
            width="100%",
            padding_x="4",
        ),
        
        # Styling
        border_bottom="1px solid",
        border_color=rx.color("gray", 3),
        padding_y="3",
        background=rx.color("gray", 1),
        position="sticky",
        top="0",
        z_index="10",
        width="100%",
    )
