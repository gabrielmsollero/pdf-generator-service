import logging
from flask import Flask
from flask.logging import default_handler


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    # include PID for clarity when using uWSGI
    default_handler.setFormatter(logging.Formatter(r"[%(asctime)s] [PID: %(process)d] [%(levelname)s] %(message)s"))

    from app.api.routes import blueprint

    app.register_blueprint(blueprint, url_prefix="/")

    return app
