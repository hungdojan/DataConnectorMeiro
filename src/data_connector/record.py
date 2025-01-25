from __future__ import annotations
import logging
import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Record:
    """Customer record entity."""

    name: str
    age: int
    # UUID of the customer's cookie
    cookie: str
    banner_id: int

    def __init__(self, name: str, age: int, cookie: str, banner_id: int):
        self.name = name
        self.age = age
        self.cookie = cookie
        self.banner_id = banner_id

    def validate(self, min_age: int | None = None, max_age: int | None = None) -> bool:
        """Validates the format of the received data.

        These are the following rules:
            - the name contains only letters and spaces
            - check for the customer's age
            - banner_id value is between 0 and 99

        The age filters are used in this order: function parameter, environment variable.
        default values (for minimum it's 18, and for maximum is not limited).

        :param (int | None) min_age: Minimal age filter. If not set, the default
            value is taken from `MIN_AGE_FILTER` environment variable.
        :param (int | None) max_age: Maximal age filter. If not set, the default
            value is taken form `MAX_AGE_FILTER` environment variable.
        :return: True if the record passes the validation test.
        :rtype: bool
        """

        # setup minimum and maximum age
        if not min_age:
            min_age = int(os.getenv("MIN_AGE_FILTER", 18))
        if not max_age:
            if os.getenv('MAX_AGE_FILTER'):
                max_age = int(os.getenv('MAX_AGE_FILTER'))

        def skip_warn(cookie_uuid: str, reason: str):
            logging.warning(f"Skipping record {cookie_uuid}: {reason}")

        if re.search(r"^[a-zA-Z ]*$", self.name) is None:
            skip_warn(self.cookie, "An invalid name.")
            return False
        if self.age < min_age:
            skip_warn(self.cookie, "Ignored due to age.")
            return False
        if max_age and self.age > int(max_age):
            skip_warn(self.cookie, "Ignored due to age.")
            return False
        if not (0 <= self.banner_id and self.banner_id <= 99):
            skip_warn(self.cookie, "Banner ID out of range.")
            return False
        return True

    def transform_data(self) -> dict[str, Any]:
        """Transform the data to the ShowAds API's format.

        :return: An object in ShowAds API format.
        :rtype: dict[str, Any]
        """
        return {"VisitorCookie": self.cookie, "BannerId": self.banner_id}

    def to_csv_string(self) -> str:
        return f"{self.name},{self.age},{self.cookie},{self.banner_id}"
