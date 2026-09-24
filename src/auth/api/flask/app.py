import atexit

from flask import Flask

from auth.api.flask.errors import register_error_handlers
from auth.api.flask.routes import register_auth_routes, register_key_routes


def create_app(container_factory):
    flask_app = Flask(__name__)
    container = container_factory()

    register_auth_routes(flask_app, container.auth_service)
    register_key_routes(flask_app, container.key_service)

    register_error_handlers(flask_app)

    atexit.register(container.close)

    return flask_app
