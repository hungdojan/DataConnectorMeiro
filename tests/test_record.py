import logging

from data_connector.record import Record


def test_validate_record(caplog):
    caplog.set_level(logging.WARNING)
    assert not Record("invalid1", 18, "uuid", 0).validate()
    assert "Skipping record" in caplog.text
    assert "An invalid name." in caplog.text

    assert not Record("invalid age", 9, "uuid", 0).validate()
    assert "Skipping record" in caplog.text
    assert "Ignored due to age." in caplog.text

    assert not Record("invalid banner id", 18, "uuid", 101).validate()
    assert "Skipping record" in caplog.text
    assert "Banner ID out of range." in caplog.text

    assert Record("valid customer", 18, "uuid", 0).validate()


def test_transform():

    data = Record("Valid Customer", 50, "cookie", 9).transform_data()
    assert {"VisitorCookie", "BannerId"} == set(data.keys())
    assert data["VisitorCookie"] == "cookie"
    assert data["BannerId"] == 9
