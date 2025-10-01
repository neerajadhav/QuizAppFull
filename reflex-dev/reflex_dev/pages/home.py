import reflex as rx
from ..components.layout import layout


def home() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("Hi, I'm Neeraj 👋", size="9"),
            rx.text("Welcome to my portfolio site!", size="5"),
            rx.link(
                rx.button("Learn more about me"),
                href="/about",
            ),
            spacing="5",
            justify="center",
            min_height="70vh",
        )
    )
