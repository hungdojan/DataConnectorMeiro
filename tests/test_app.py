from pathlib import Path

from flask.testing import FlaskCliRunner
from flask_restx.api import HTTPStatus

from data_connector.commands import upload_file


def test_send_record_api(client, mock_ok):
    with mock_ok:
        res = client.post("/send_record", json={})
        assert res.status_code == HTTPStatus.BAD_REQUEST

        res = client.post(
            "/send_record",
            json={"name": "Mario", "age": 10, "cookie": "id", "banner_id": 10},
        )
        assert res.status_code == HTTPStatus.ACCEPTED
        assert "did not pass" in res.json["message"]

        res = client.post(
            "/send_record",
            json={"name": "Mario", "age": 18, "cookie": "id", "banner_id": 10},
        )
        assert res.status_code == HTTPStatus.ACCEPTED
        assert res.json["message"] == "Record id sent to ShowAPI."


def test_send_bulk_api(client, mock_ok):
    filepath = f"{Path(__file__).parent.resolve()}/resources/test_data.csv"
    data = {"file": (open(filepath, "rb"), filepath)}
    with mock_ok:
        res = client.post("/send_record/bulk", data=data)
        assert res.status_code == HTTPStatus.ACCEPTED
        assert res.json["sent"] == 3


def test_cli_upload_file(cli: FlaskCliRunner, mock_ok):
    filepath = f"{Path(__file__).parent.resolve()}/resources/test_data.csv"
    result = cli.invoke(upload_file, ["file.txt"])
    assert result.exit_code == 1

    with mock_ok:
        result = cli.invoke(upload_file, [filepath])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully sent 3 of records."

        result = cli.invoke(upload_file, ["-mi", 8, filepath])
        assert result.exit_code == 0
        assert result.output.strip() == "Successfully sent 4 of records."

        result = cli.invoke(upload_file, ["-ma", 30, filepath])
        assert result.exit_code == 0
        # default min age is set to 18
        assert result.output.strip() == "Successfully sent 2 of records."

        result = cli.invoke(upload_file, ["-mi", 20, "-ma", 30, filepath])
        assert result.exit_code == 0
        # default min age is set to 18
        assert result.output.strip() == "Successfully sent 2 of records."
