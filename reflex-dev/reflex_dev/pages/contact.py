import reflex as rx


def contact() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Contact", size="9"),
            rx.text("Feel free to reach out!"),
            rx.text("📧 neeraj@example.com"),
            rx.link(
                rx.button("Back to Home"),
                href="/",
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        )
    )
