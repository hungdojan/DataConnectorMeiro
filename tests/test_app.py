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

        res = client.post(
            "/send_record",
            json={
                "name": "Mario",
                "age": 10,
                "cookie": "id",
                "banner_id": 10,
                "min_age": 20,
            },
        )
        assert res.status_code == HTTPStatus.ACCEPTED
        assert "did not pass" in res.json["message"]


def test_send_bulk_api(client, mock_ok):
    filepath = Path(__file__).parent / "resources" / "test_data.csv"
    with mock_ok:
        with open(filepath, "rb") as f:
            res = client.post("/send_record/bulk", data={"file": (f, filepath)})
            assert res.status_code == HTTPStatus.ACCEPTED
            assert res.json["sent"] == 3

        with open(filepath, "rb") as f:
            res = client.post(
                "/send_record/bulk", data={"file": (f, filepath), "max_age": 30}
            )
            assert res.status_code == HTTPStatus.ACCEPTED
            assert res.json["sent"] == 2

        with open(filepath, "rb") as f:
            res = client.post(
                "/send_record/bulk", data={"file": (f, filepath), "min_age": 30}
            )
            assert res.status_code == HTTPStatus.ACCEPTED
            assert res.json["sent"] == 1

        with open(filepath, "rb") as f:
            res = client.post(
                "/send_record/bulk",
                data={"file": (f, filepath), "min_age": 27, "max_age": 30},
            )
            assert res.status_code == HTTPStatus.ACCEPTED
            assert res.json["sent"] == 0


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
