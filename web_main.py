"""
Entry point for the web interface of the Todo App.
"""
from dotenv import load_dotenv

from src.infrastructure.configuration.container import create_application
from src.infrastructure.web.app import create_web_app
from src.interfaces.presenters.broker_presenter import WebBrokerPresenter
from src.interfaces.presenters.dispatch_presenter import WebDispatchPresenter
from src.interfaces.presenters.driver_presenter import WebDriverPresenter
from src.interfaces.presenters.location_presenter import WebLocationPresenter
from src.interfaces.presenters.task_presenter import WebTaskPresenter


load_dotenv()

def main():
    """Create and run the Flask web application."""

    app_container = create_application(
        broker_presenter=WebBrokerPresenter(),
        dispatch_presenter=WebDispatchPresenter(),
        driver_presenter=WebDriverPresenter(),
        location_presenter=WebLocationPresenter(),
        task_presenter=WebTaskPresenter()
    )
    web_app = create_web_app(app_container)
    web_app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )


if __name__ == "__main__":
    main()
