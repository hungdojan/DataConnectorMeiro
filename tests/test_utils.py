from pathlib import Path

from data_connector.record import Record
from data_connector.utils import allowed_file_extension, parse_file, parse_line


def test_parse_line():
    rec = Record("Name", 18, "Cookie", 20)
    line = rec.to_csv_string()

    new_rec = parse_line(line)
    assert new_rec
    assert rec.name == new_rec.name
    assert rec.age == new_rec.age
    assert rec.cookie == new_rec.cookie
    assert rec.banner_id == new_rec.banner_id


def test_parse_file():
    filepath = Path(__file__).parent / "resources" / "test_data.csv"
    with open(filepath, "rb") as f:
        buffer = parse_file(f, None, None)
    assert len(buffer) == 3
    assert buffer[0].cookie == "jjjj"
    assert buffer[1].cookie == "ffff"


def test_allowed_file_extension():
    assert not allowed_file_extension("file.txt")
    assert allowed_file_extension("file.csv")
