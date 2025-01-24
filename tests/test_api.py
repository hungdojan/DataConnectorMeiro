import io
from pathlib import Path

from flask_restx.api import HTTPStatus


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
        assert res.json["sent"] == 2
