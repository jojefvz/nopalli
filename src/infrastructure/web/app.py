from flask import Flask

from src.infrastructure.configuration.container import Application


def create_web_app(app_container: Application) -> Flask:
    """Create and configure Flask application."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # Change this in production
    flask_app.config["APP_CONTAINER"] = app_container  # Store container in config

    # Register blueprints
    from .routes.broker import bp as broker_bp
    flask_app.register_blueprint(broker_bp)

    from .routes.driver import bp as driver_bp
    flask_app.register_blueprint(driver_bp)

    from .routes.dispatch import bp as dispatch_bp
    flask_app.register_blueprint(dispatch_bp)

    from .routes.home import bp as home_bp
    flask_app.register_blueprint(home_bp)

    from .routes.location import bp as location_bp
    flask_app.register_blueprint(location_bp)

    return flask_app
