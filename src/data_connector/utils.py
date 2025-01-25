from __future__ import annotations

import logging
import os
from datetime import date

from data_connector.record import Record


def parse_line(line: str) -> Record | None:
    """Parse a single line from CSV file.

    :param str line: A line from the file.

    :return: Constructed Record object; None if failed.
    :rtype: Record | None
    """
    data = line.strip().split(",")

    # can throw an exception
    try:
        rec = Record(data[0], int(data[1]), data[2], int(data[3]))
        logging.debug(f"Record {rec.cookie} loaded.")
        return rec
    except (TypeError, ValueError):
        logging.warning(f"Error while parsing data: {data}")
        return None


def parse_file(file, min_age: int | None, max_age: int | None) -> list[Record]:
    """Parse a file and return a buffer of records."""
    buffer: list[Record] = []
    for line in file:
        rec = parse_line(line.decode().strip())
        if rec and rec.validate(min_age, max_age):
            buffer.append(rec)
    return buffer


def allowed_file_extension(filename: str) -> bool:
    """Check if the given file is CSV format."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "csv"


def store_unsent_records(lof_records: list[Record]):
    """Save (unsent) records to the CSV file for later resend.

    The data are stored in a file at `FAILED_RECORDS_DIRPATH/unsent_{date}.csv`.
    """
    failed_records_dirpath = os.getenv("FAILED_RECORDS_DIRPATH", "/tmp")
    with open(f"{failed_records_dirpath}/unsent_{date.today()}.csv", "a+") as f:
        for record in lof_records:
            f.write(f"{record.to_csv_string()}\n")
