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

    def validate(self) -> bool:
        """Validates the format of the received data.

        These are the following rules:
            - the name contains only letters and spaces
            - check for the customer's age
            - banner_id value is between 0 and 99

        :return: True if the record passes the validation test.
        :rtype: bool
        """

        def skip_warn(cookie_uuid: str, reason: str):
            logging.warning(f"Skipping record {cookie_uuid}: {reason}")

        if re.search(r"^[a-zA-Z ]*$", self.name) is None:
            skip_warn(self.cookie, "An invalid name.")
            return False
        if self.age < int(os.getenv("DC_AGE_FILTERING", 18)):
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
