from __future__ import annotations

import click
from flask.cli import with_appcontext

from data_connector.show_ads_api_wrapper import send_data
from data_connector.utils import allowed_file_extension, parse_file


@click.command(name="upload-file")
@click.option("-mi", "--minimum", help="Minimum age filter", type=int)
@click.option("-ma", "--maximum", help="Maximum age filter", type=int)
@click.argument("filename")
@with_appcontext
def upload_file(minimum: int | None, maximum: int | None, filename: str):
    """CLI command to process CSV file.

    :param str filename: File path to the CSV file.
    """
    if not allowed_file_extension(filename):
        click.echo("Only CSV file format is supported.")
        exit(1)

    buffer = []
    with open(filename, "rb") as f:
        buffer = parse_file(f, minimum, maximum)
    nof_recs = send_data(buffer)
    click.echo(f"Successfully sent {nof_recs} of records.")
