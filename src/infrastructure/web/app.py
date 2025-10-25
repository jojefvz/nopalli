from flask import Flask

from ..configuration.container import Application


def create_web_app(app_container: Application) -> Flask:
    """Create and configure Flask application."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # Change this in production
    flask_app.config["APP_CONTAINER"] = app_container  # Store container in config

    # Register blueprints
    from .location import bp as location_bp

    flask_app.register_blueprint(location_bp)

    return flask_app
