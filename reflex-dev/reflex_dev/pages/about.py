import reflex as rx
from ..components.layout import layout


def about() -> rx.Component:
    return rx.layout(
        rx.vstack(
            rx.heading("About Me", size="9"),
            rx.text(
                "I'm a postgraduate student and aspiring GCP freelancer. "
                "I love working on cloud, NLP, and building apps with Reflex."
            ),
            rx.link(
                rx.button("Contact Me"),
                href="/contact",
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        )
    )
