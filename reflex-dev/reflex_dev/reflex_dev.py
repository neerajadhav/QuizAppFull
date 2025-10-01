import reflex as rx
from .pages import home, about, contact


class State(rx.State):
    """Global app state."""


app = rx.App()

# Register portfolio pages
app.add_page(home, route="/")
app.add_page(about, route="/about")
app.add_page(contact, route="/contact")
