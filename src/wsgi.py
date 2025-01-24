import logging

from flask import Flask

from .api import data_connector_api

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


def create_app() -> Flask:
    app = Flask(__name__)
    data_connector_api.init_app(app)
    return app


app = create_app()
