from __future__ import annotations

import logging as log

from flask_restx import Api, Namespace, Resource, fields
from flask_restx.api import HTTPStatus
from flask_restx.reqparse import FileStorage

from .record import Record
from .show_ads_api_wrapper import send_data, send_record


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
        log.debug(f"Record {rec.cookie} loaded.")
        return rec
    except (TypeError, ValueError):
        log.warning(f"Error while parsing data: {data}")
        return None


# init API
data_connector_api = Api(title="DataConnectorAPI", version="1.0.0")
send_record_ns = Namespace(
    "SendCustomerRecord",
    description="Process data and send them to ShowAds API.",
    path="/",
)
data_connector_api.add_namespace(send_record_ns)

# parser to process file upload
file_parser = send_record_ns.parser()
file_parser.add_argument("file", location="files", type=FileStorage, required=True)


@send_record_ns.route("/send_record")
@send_record_ns.doc(description="Send a single customer record.")
class SendRecord(Resource):
    @send_record_ns.expect(
        send_record_ns.model(
            "Record",
            {
                "name": fields.String,
                "age": fields.Integer,
                "cookie": fields.String,
                "banner_id": fields.Integer,
            },
        ),
        validate=True,
    )
    @send_record_ns.response(
        code=HTTPStatus.ACCEPTED,
        description="Successfully received data.",
        model=fields.String,
        envelope="message",
    )
    @send_record_ns.response(
        code=HTTPStatus.BAD_REQUEST,
        description="Failed to process received data.",
        model=fields.String,
        envelope="message",
    )
    def post(self):
        data = send_record_ns.payload
        try:
            rec = Record(**data)
        except TypeError:
            log.error(
                "/send_record: Failed to transform received data to Record object."
            )
            log.error(f"/send_record: {data}.")
            return {"message": "Failed to process data."}, HTTPStatus.BAD_REQUEST
        msg = f"Record {rec.cookie} did not pass the validation, ignored."
        if rec.validate():
            log.debug(f"/send_record: Sending {rec.cookie} to ShowAds API.")
            send_record(rec)
            msg = f"Record {rec.cookie} sent to ShowAPI."
        return {"message": msg}, HTTPStatus.ACCEPTED


@send_record_ns.route("/send_record/bulk")
@send_record_ns.doc(description="Send a bulk of records using a CSV file.")
class SendBulk(Resource):
    @send_record_ns.doc(parser=file_parser)
    @send_record_ns.response(
        code=HTTPStatus.ACCEPTED,
        description="Number of sent records.",
        model=fields.Integer,
        envelope="sent",
    )
    def post(self):
        args = file_parser.parse_args()
        upload_file: FileStorage = args["file"]
        buffer: list[Record] = []
        for line in upload_file:
            rec = parse_line(line.decode())
            if rec and rec.validate():
                buffer.append(rec)

        nof_recs = send_data(buffer)
        return {"sent": nof_recs}, HTTPStatus.ACCEPTED
