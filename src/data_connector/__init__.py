from __future__ import annotations

from flask import Flask
from data_connector.api import data_connector_api
from data_connector.commands import upload_file


def create_app() -> Flask:
    app = Flask(__name__)
    data_connector_api.init_app(app)
    app.cli.add_command(upload_file)
    return app
