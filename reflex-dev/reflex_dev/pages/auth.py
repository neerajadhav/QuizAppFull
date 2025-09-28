"""Authentication pages (login and register)."""

import reflex as rx
from reflex_dev.components.layout import auth_layout
from reflex_dev.components.forms import login_form, register_form


def login_page() -> rx.Component:
    """Login page."""
    return auth_layout(
        login_form(),
    )


def register_page() -> rx.Component:
    """Registration page."""
    return auth_layout(
        register_form(),
    )
