from __future__ import annotations

import os
from typing import Iterator

import pytest
import requests
import requests_mock
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from data_connector.show_ads_api_wrapper import OPT_DICT
from data_connector import create_app


def single_rec_callback(
    request: requests.Request, context: requests_mock.Context
) -> dict:
    # testing unauthorized access
    auth: str = request.headers.get("Authorization", "")
    # check if the Authorization fields is not empty and the Bearer has a valid data
    context.status_code = 200 if auth and auth.replace("Bearer", "").strip() else 401
    return {}


def bulk_callback(request: requests.Request, context: requests_mock.Context) -> dict:
    # testing unauthorized access
    auth = request.headers.get("Authorization")
    # check if the Authorization fields is not empty and the Bearer has a valid data
    context.status_code = 200 if auth and auth.replace("Bearer", "").strip() else 401
    return {}


@pytest.fixture
def mock_ok() -> Iterator[requests_mock.Mocker]:
    # nullify the token
    OPT_DICT["access_token"] = ""

    mock = requests_mock.Mocker()
    mock.register_uri(
        "POST", f"{os.getenv('API_URL')}/auth", json={"AccessToken": "access-token"}
    )
    mock.register_uri(
        "POST", f"{os.getenv('API_URL')}/banners/show", json=single_rec_callback
    )
    mock.register_uri(
        "POST", f"{os.getenv('API_URL')}/banners/show/bulk", json=bulk_callback
    )
    yield mock


@pytest.fixture
def mock_fail() -> Iterator[requests_mock.Mocker]:
    # nullify the token
    OPT_DICT["access_token"] = ""

    mock = requests_mock.Mocker()
    mock.register_uri("POST", f"{os.getenv('API_URL')}/auth", json={}, status_code=500)
    mock.register_uri(
        "POST", f"{os.getenv('API_URL')}/banners/show", json=single_rec_callback
    )
    mock.register_uri(
        "POST", f"{os.getenv('API_URL')}/banners/show/bulk", json=bulk_callback
    )
    yield mock


@pytest.fixture
def app() -> Iterator[Flask]:
    app = create_app()
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def cli(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
