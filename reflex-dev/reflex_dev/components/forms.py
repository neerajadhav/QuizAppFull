"""Form components for authentication."""

import reflex as rx
from reflex_dev.auth.auth_state import AuthState


def login_form() -> rx.Component:
    """Create a login form."""
    return rx.card(
        rx.vstack(
            rx.heading("Login", size="6", text_align="center"),
            
            # Error message
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="circle_alert",
                    color_scheme="red",
                    size="1",
                ),
            ),
            
            # User ID field
            rx.vstack(
                rx.text("User ID", size="3", weight="medium"),
                rx.input(
                    placeholder="Enter your Student ID or Teacher ID",
                    value=AuthState.login_user_id,
                    on_change=AuthState.set_login_user_id,
                    type="text",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Password field
            rx.vstack(
                rx.text("Password", size="3", weight="medium"),
                rx.input(
                    placeholder="Enter your password",
                    value=AuthState.login_password,
                    on_change=AuthState.set_login_password,
                    type="password",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Login button
            rx.button(
                "Login",
                on_click=AuthState.login,
                size="3",
                width="100%",
                variant="solid",
            ),
            
            # Register link
            rx.text(
                "Don't have an account? ",
                rx.link("Register here", href="/register", color=rx.color("blue", 9)),
                size="2",
                text_align="center",
            ),
            
            spacing="4",
            width="100%",
        ),
        max_width="400px",
        padding="6",
    )


def register_form() -> rx.Component:
    """Create a registration form."""
    return rx.card(
        rx.vstack(
            rx.heading("Register", size="6", text_align="center"),
            
            # Error message
            rx.cond(
                AuthState.error_message != "",
                rx.callout(
                    AuthState.error_message,
                    icon="circle_alert",
                    color_scheme=rx.cond(
                        AuthState.error_message.contains("failed"),
                        "red",
                        "green"
                    ),
                    size="1",
                ),
            ),
            
            # Role selection
            rx.vstack(
                rx.text("I am a:", size="3", weight="medium"),
                rx.radio_group(
                    ["student", "teacher"],
                    value=AuthState.register_role,
                    on_change=AuthState.set_register_role,
                ),
                spacing="2",
                width="100%",
            ),
            
            # User ID field
            rx.vstack(
                rx.text(
                    rx.cond(
                        AuthState.register_role == "student",
                        "Student ID",
                        "Teacher ID"
                    ),
                    size="3",
                    weight="medium"
                ),
                rx.input(
                    placeholder=rx.cond(
                        AuthState.register_role == "student",
                        "e.g., STU123456",
                        "e.g., TCH123456"
                    ),
                    value=AuthState.register_user_id,
                    on_change=AuthState.set_register_user_id,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Email field
            rx.vstack(
                rx.text("Email", size="3", weight="medium"),
                rx.input(
                    placeholder="Enter your email",
                    value=AuthState.register_email,
                    on_change=AuthState.set_register_email,
                    type="email",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Full name field
            rx.vstack(
                rx.text("Full Name", size="3", weight="medium"),
                rx.input(
                    placeholder="Enter your full name",
                    value=AuthState.register_full_name,
                    on_change=AuthState.set_register_full_name,
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Role-specific fields
            rx.cond(
                AuthState.register_role == "student",
                # Student fields
                rx.vstack(
                    rx.vstack(
                        rx.text("Program", size="3", weight="medium"),
                        rx.input(
                            placeholder="e.g., Computer Science",
                            value=AuthState.register_program,
                            on_change=AuthState.set_register_program,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Year", size="3", weight="medium"),
                            rx.select(
                                ["1", "2", "3", "4"],
                                value=str(AuthState.register_year_of_study),
                                on_change=AuthState.set_register_year_of_study,
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Semester", size="3", weight="medium"),
                            rx.select(
                                ["1", "2"],
                                value=str(AuthState.register_semester),
                                on_change=AuthState.set_register_semester,
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                # Teacher fields
                rx.vstack(
                    rx.vstack(
                        rx.text("Department", size="3", weight="medium"),
                        rx.input(
                            placeholder="e.g., Computer Science",
                            value=AuthState.register_department,
                            on_change=AuthState.set_register_department,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Specialization (Optional)", size="3", weight="medium"),
                        rx.input(
                            placeholder="e.g., Machine Learning",
                            value=AuthState.register_specialization,
                            on_change=AuthState.set_register_specialization,
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            
            # Password fields
            rx.vstack(
                rx.text("Password", size="3", weight="medium"),
                rx.input(
                    placeholder="Enter your password",
                    value=AuthState.register_password,
                    on_change=AuthState.set_register_password,
                    type="password",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            rx.vstack(
                rx.text("Confirm Password", size="3", weight="medium"),
                rx.input(
                    placeholder="Confirm your password",
                    value=AuthState.register_confirm_password,
                    on_change=AuthState.set_register_confirm_password,
                    type="password",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Register button
            rx.button(
                "Register",
                on_click=AuthState.register,
                size="3",
                width="100%",
                variant="solid",
            ),
            
            # Login link
            rx.text(
                "Already have an account? ",
                rx.link("Login here", href="/login", color=rx.color("blue", 9)),
                size="2",
                text_align="center",
            ),
            
            spacing="4",
            width="100%",
        ),
        max_width="500px",
        padding="6",
    )
