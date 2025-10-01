import reflex as rx


def header() -> rx.Component:
    return rx.hstack(
        rx.link("Home", href="/"),
        rx.link("About", href="/about"),
        rx.link("Contact", href="/contact"),
        spacing="4",
        padding="1em",
        justify="center",
        border_bottom="1px solid lightgray",
    )
