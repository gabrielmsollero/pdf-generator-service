from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.api.routes import blueprint

    app.register_blueprint(blueprint, url_prefix="/")

    return app
