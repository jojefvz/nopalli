"""
Entry point for the web interface of the Todo App.
"""

from src.infrastructure.configuration.container import create_application
from src.infrastructure.web.app import create_web_app
from src.interfaces.presenters.location_presenter import WebLocationPresenter


def main():
    """Create and run the Flask web application."""

    app_container = create_application(
        location_presenter=WebLocationPresenter(),
    )
    web_app = create_web_app(app_container)
    web_app.run(debug=True)


if __name__ == "__main__":
    main()
