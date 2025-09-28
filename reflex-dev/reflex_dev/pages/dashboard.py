"""Dashboard pages for teachers and students."""

import reflex as rx
from reflex_dev.components.layout import dashboard_layout
from reflex_dev.components.cards import stats_card, user_card, quiz_card
from reflex_dev.auth.auth_state import AuthState


def teacher_dashboard() -> rx.Component:
    """Teacher dashboard page."""
    return dashboard_layout(
        "Teacher Dashboard",
        
        # Welcome section
        rx.vstack(
            rx.heading(f"Welcome back, {AuthState.user_display_name}!", size="6"),
            rx.text("Here's an overview of your teaching activities", size="3", color=rx.color("gray", 10)),
            spacing="2",
            align="start",
        ),
        
        # Stats cards
        rx.grid(
            stats_card("Active Quizzes", "12", "clipboard-list", "blue"),
            stats_card("Total Students", "245", "users", "green"),
            stats_card("Completed Quizzes", "8", "circle-check", "purple"),
            stats_card("Average Score", "78%", "bar-chart", "orange"),
            columns="4",
            spacing="4",
            width="100%",
        ),
        
        # Quick actions
        rx.vstack(
            rx.heading("Quick Actions", size="4"),
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon("plus", size=18),
                        "Create New Quiz",
                        size="3",
                        variant="solid",
                    ),
                    href="/teacher/quiz/create",
                ),
                rx.link(
                    rx.button(
                        rx.icon("eye", size=18),
                        "View All Quizzes",
                        size="3",
                        variant="outline",
                    ),
                    href="/teacher/quizzes",
                ),
                rx.link(
                    rx.button(
                        rx.icon("download", size=18),
                        "Export Results",
                        size="3",
                        variant="outline",
                    ),
                    href="/teacher/export",
                ),
                spacing="3",
            ),
            spacing="3",
            align="start",
        ),
        
        # Recent quizzes
        rx.vstack(
            rx.heading("Recent Quizzes", size="4"),
            rx.grid(
                quiz_card({
                    "title": "Python Basics Quiz",
                    "description": "Test your knowledge of Python fundamentals",
                    "status": "Active",
                    "duration": 45,
                    "questions": 20,
                    "role": "teacher"
                }),
                quiz_card({
                    "title": "Data Structures Quiz",
                    "description": "Arrays, linked lists, and more",
                    "status": "Draft",
                    "duration": 60,
                    "questions": 25,
                    "role": "teacher"
                }),
                quiz_card({
                    "title": "Algorithms Quiz",
                    "description": "Sorting and searching algorithms",
                    "status": "Active",
                    "duration": 90,
                    "questions": 30,
                    "role": "teacher"
                }),
                columns="3",
                spacing="4",
                width="100%",
            ),
            spacing="3",
            align="start",
        ),
    )


def student_dashboard() -> rx.Component:
    """Student dashboard page."""
    return dashboard_layout(
        "Student Dashboard",
        
        # Welcome section
        rx.vstack(
            rx.heading(f"Welcome back, {AuthState.user_display_name}!", size="6"),
            rx.text("Continue your learning journey", size="3", color=rx.color("gray", 10)),
            spacing="2",
            align="start",
        ),
        
        # Stats cards
        rx.grid(
            stats_card("Quizzes Taken", "15", "clipboard-check", "blue"),
            stats_card("Average Score", "82%", "trending-up", "green"),
            stats_card("Available Quizzes", "8", "clock", "purple"),
            stats_card("Rank in Class", "#12", "trophy", "orange"),
            columns="4",
            spacing="4",
            width="100%",
        ),
        
        # Available quizzes
        rx.vstack(
            rx.heading("Available Quizzes", size="4"),
            rx.grid(
                quiz_card({
                    "title": "Python Basics Quiz",
                    "description": "Test your knowledge of Python fundamentals",
                    "status": "Available",
                    "duration": 45,
                    "questions": 20,
                    "role": "student"
                }),
                quiz_card({
                    "title": "Data Structures Quiz",
                    "description": "Arrays, linked lists, and more",
                    "status": "Available",
                    "duration": 60,
                    "questions": 25,
                    "role": "student"
                }),
                quiz_card({
                    "title": "Web Development Quiz",
                    "description": "HTML, CSS, and JavaScript basics",
                    "status": "Available",
                    "duration": 50,
                    "questions": 22,
                    "role": "student"
                }),
                columns="3",
                spacing="4",
                width="100%",
            ),
            spacing="3",
            align="start",
        ),
        
        # Recent results
        rx.vstack(
            rx.heading("Recent Results", size="4"),
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text("Quiz Name", size="2", weight="bold", width="200px"),
                        rx.text("Score", size="2", weight="bold", width="100px"),
                        rx.text("Date", size="2", weight="bold", width="120px"),
                        rx.text("Status", size="2", weight="bold"),
                        justify="between",
                        width="100%",
                    ),
                    rx.separator(),
                    rx.hstack(
                        rx.text("Algorithms Quiz", size="2", width="200px"),
                        rx.text("85%", size="2", color=rx.color("green", 9), width="100px"),
                        rx.text("2024-01-15", size="2", width="120px"),
                        rx.badge("Passed", color_scheme="green"),
                        justify="between",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Database Quiz", size="2", width="200px"),
                        rx.text("78%", size="2", color=rx.color("green", 9), width="100px"),
                        rx.text("2024-01-12", size="2", width="120px"),
                        rx.badge("Passed", color_scheme="green"),
                        justify="between",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("OOP Concepts", size="2", width="200px"),
                        rx.text("92%", size="2", color=rx.color("green", 9), width="100px"),
                        rx.text("2024-01-10", size="2", width="120px"),
                        rx.badge("Excellent", color_scheme="blue"),
                        justify="between",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="4",
                width="100%",
            ),
            spacing="3",
            align="start",
        ),
    )
