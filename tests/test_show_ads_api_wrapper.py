from __future__ import annotations

from data_connector.record import Record
from data_connector.show_ads_api_wrapper import (
    OPT_DICT,
    send_bulk,
    send_data,
    send_record,
    update_access_token,
)


def test_update_access_token(mock_ok):
    assert not OPT_DICT["access_token"]
    with mock_ok:
        update_access_token()
    assert OPT_DICT["access_token"]


def test_send_record(mock_ok):
    rec = Record("Mario", 25, "itsmemario", 40)
    with mock_ok:
        assert send_record(rec) == 1


def test_send_bulk(mock_ok):
    recs = [Record("gumba", 20, "chompchomp", 2) for _ in range(100)]
    with mock_ok:
        assert send_bulk(1, recs) == len(recs)


def test_send_data(mock_ok):
    recs = [Record("gumba", 20, "chompchomp", 2) for _ in range(1200)]
    with mock_ok:
        assert send_data(recs) == len(recs)


def test_send_fail(mock_fail):
    recs = [Record("gumba", 20, "chompchomp", 2) for _ in range(1200)]
    with mock_fail:
        assert send_record(recs[0]) == 0
        assert send_data(recs) == 0
