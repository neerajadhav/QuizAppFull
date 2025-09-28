"""QuizApp - A modular reflex application with role-based authentication."""

import reflex as rx
from rxconfig import config

# Import components and pages
from reflex_dev.auth.auth_state import AuthState
from reflex_dev.pages.home import home_page
from reflex_dev.pages.auth import login_page, register_page
from reflex_dev.pages.dashboard import teacher_dashboard, student_dashboard
from reflex_dev.pages.profile import profile_page
from reflex_dev.database import init_db

# Import auth utilities
from reflex_dev.auth.decorators import require_teacher_component, require_student_component


# Initialize database
init_db()

# Create the app
app = rx.App()

# Add pages
app.add_page(home_page, route="/")
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(profile_page, route="/profile")

# Protected pages
app.add_page(teacher_dashboard, route="/teacher/dashboard")
app.add_page(student_dashboard, route="/student/dashboard")

# Placeholder pages for future functionality
def create_quiz_page() -> rx.Component:
    """Placeholder for create quiz page."""
    return require_teacher_component(
        rx.center(
            rx.vstack(
                rx.heading("Create Quiz", size="6"),
                rx.text("Quiz creation functionality coming soon!"),
                rx.link(
                    rx.button("Back to Dashboard"),
                    href="/teacher/dashboard",
                ),
                spacing="4",
            ),
            min_height="80vh",
        )
    )

def teacher_quizzes_page() -> rx.Component:
    """Placeholder for teacher quizzes page."""
    return require_teacher_component(
        rx.center(
            rx.vstack(
                rx.heading("My Quizzes", size="6"),
                rx.text("Quiz management functionality coming soon!"),
                rx.link(
                    rx.button("Back to Dashboard"),
                    href="/teacher/dashboard",
                ),
                spacing="4",
            ),
            min_height="80vh",
        )
    )

def student_quizzes_page() -> rx.Component:
    """Placeholder for student quizzes page."""
    return require_student_component(
        rx.center(
            rx.vstack(
                rx.heading("Available Quizzes", size="6"),
                rx.text("Quiz taking functionality coming soon!"),
                rx.link(
                    rx.button("Back to Dashboard"),
                    href="/student/dashboard",
                ),
                spacing="4",
            ),
            min_height="80vh",
        )
    )

def student_results_page() -> rx.Component:
    """Placeholder for student results page."""
    return require_student_component(
        rx.center(
            rx.vstack(
                rx.heading("My Results", size="6"),
                rx.text("Results viewing functionality coming soon!"),
                rx.link(
                    rx.button("Back to Dashboard"),
                    href="/student/dashboard",
                ),
                spacing="4",
            ),
            min_height="80vh",
        )
    )

def unauthorized_page() -> rx.Component:
    """Unauthorized access page."""
    return rx.center(
        rx.vstack(
            rx.icon("shield-x", size=64, color=rx.color("red", 9)),
            rx.heading("Unauthorized Access", size="6"),
            rx.text("You don't have permission to access this page."),
            rx.link(
                rx.button("Go Home"),
                href="/",
            ),
            spacing="4",
            align="center",
        ),
        min_height="80vh",
    )

# Add additional pages
app.add_page(create_quiz_page, route="/teacher/quiz/create")
app.add_page(teacher_quizzes_page, route="/teacher/quizzes")
app.add_page(student_quizzes_page, route="/student/quizzes")
app.add_page(student_results_page, route="/student/results")
app.add_page(unauthorized_page, route="/unauthorized")
