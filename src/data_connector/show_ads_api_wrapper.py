from __future__ import annotations

import logging
import os
from typing import Any

import requests

from data_connector.record import Record
from data_connector.utils import store_unsent_records

OPT_DICT: dict[str, Any] = {
    "base_url": os.getenv("API_URL"),
    "project_key": os.getenv("PROJECT_KEY"),
    "access_token": "",
}


def send_data(buffer: list[Record]) -> int:
    """Send a list of records to the ShowAds API.

    :param list[Record] buffer: A list containing all the valid records.
    :return: Number of records sent.
    :rtype: int
    """
    total_sent = 0
    i = 0
    while i <= len(buffer) // 1000:
        # send a bulk of max 1000 records
        total_sent += send_bulk(i, buffer[i * 1000 : min((i + 1) * 1000, len(buffer))])
        i += 1
    return total_sent


def update_access_token(nof_tries: int = 3):
    """Updates an access token.

    Requires the project key to be set.

    :param int nof_tries: Number of tries.
    """

    def warning_msg(reason: str):
        logging.warning(f"Access Token request fail: {reason}")

    res = requests.post(
        f"{OPT_DICT['base_url']}/auth", json={"ProjectKey": OPT_DICT["project_key"]}
    )
    tries = 0
    while res.status_code != 200 and (nof_tries == -1 or tries < nof_tries):
        if res.status_code == 400:
            warning_msg("Project Key missing.")
        elif res.status_code == 500:
            warning_msg("Internal server error.")
        elif res.status_code == 429:
            warning_msg("Too many requests.")
        else:
            warning_msg(f"Request return code {res.status_code}.")
        tries += 1

    if res.status_code != 200:
        logging.error("Access Token request fail: Unable to fetch auth token.")
        return
    logging.debug("Access Token loaded")
    OPT_DICT["access_token"] = res.json()["AccessToken"]


def send_bulk(bulk_id: int, lof_records: list[Record]) -> int:
    """Wrapper function that sends a bulk of customer records to ShowAds API endpoint.

    The sender must ensure to send the maximum number of records allowed by the API.
    """
    rec_sent = 0
    session = requests.session()
    if not OPT_DICT["access_token"]:
        update_access_token()

    headers = {"Authorization": f"Bearer {OPT_DICT['access_token']}"}
    session.headers.update(headers)

    retries = 3
    while retries > 0:
        res = session.post(
            f"{OPT_DICT['base_url']}/banners/show/bulk",
            json={"Data": [r.transform_data() for r in lof_records]},
        )
        if res.status_code == 200:
            logging.debug(f"Send bulk {bulk_id}: A bulk successfully sent.")
            rec_sent = len(lof_records)
            retries = 0
        elif res.status_code == 401:
            update_access_token()
        elif res.status_code == 400:
            logging.error(f"Send bulk {bulk_id} fail: Bad request.")
        elif res.status_code == 500:
            logging.error(f"Send bulk {bulk_id} fail: Destination server error.")
        else:
            logging.error(f"Send bulk {bulk_id} fail: Return code {res.status_code}.")
        retries -= 1

    # app was unable to forward data to ShowAds API
    # thus we store it in CSV file (for convenience)
    # and try it later
    if rec_sent == 0:
        store_unsent_records(lof_records)
    return rec_sent


def send_record(rec: Record) -> int:
    """Wrapper function that sends a single customer record to ShowAds API endpoint.

    The function has 3 retries. If all three attempts fail

    :param Record rec: The given record to be sent to the external API.
    :return: Number of records successfully sent.
    :rtype: int
    """
    rec_sent = 0
    session = requests.session()
    if not OPT_DICT["access_token"]:
        update_access_token()

    headers = {"Authorization": f"Bearer {OPT_DICT['access_token']}"}
    session.headers.update(headers)

    retries = 3
    while retries > 0:
        res = session.post(
            f"{OPT_DICT['base_url']}/banners/show", json=rec.transform_data()
        )
        if res.status_code == 200:
            rec_sent = 1
            retries = 0
        elif res.status_code == 401:
            update_access_token()
        elif res.status_code == 400:
            logging.error(f"Send record {rec.cookie} fail: Bad request.")
        elif res.status_code == 500:
            logging.error(f"Send record {rec.cookie} fail: Destination server error.")
        elif res.status_code == 429:
            logging.error(
                f"Send record {rec.cookie} fail: Destination server is under heavy load."
            )
        else:
            logging.error(
                f"Send record {rec.cookie} fail: Return code {res.status_code}."
            )

        retries -= 1
    # app was unable to forward data to ShowAds API
    # thus we store it in CSV file (for convenience)
    # and try it later
    if rec_sent == 0:
        store_unsent_records([rec])
    return rec_sent
