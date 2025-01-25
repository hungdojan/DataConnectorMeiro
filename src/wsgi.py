from __future__ import annotations

import logging
import os

from data_connector import create_app

if not os.getenv("API_URL"):
    logging.error("Environment variable API_URL not found.")
    exit(1)
if not os.getenv("PROJECT_KEY"):
    logging.error("Environment variable PROJECT_KEY not found.")
    exit(1)

app = create_app()
