import reflex as rx
from .header import header


def layout(*children) -> rx.Component:
    """A reusable page layout with a header and footer."""
    return rx.container(
        rx.vstack(
            header(),
            rx.box(*children, padding="2em"),
            rx.text("© 2025 Neeraj Portfolio", size="2", align="center", margin_top="2em"),
            spacing="4",
            min_height="100vh",
            justify="between",
        )
    )
