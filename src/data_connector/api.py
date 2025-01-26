from __future__ import annotations

import logging as log

from flask_restx import Api, Namespace, Resource, fields
from flask_restx.api import HTTPStatus
from flask_restx.reqparse import FileStorage

from .record import Record
from .show_ads_api_wrapper import send_data, send_record
from .utils import allowed_file_extension, parse_file

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
file_parser.add_argument("min_age", location="form", type=int)
file_parser.add_argument("max_age", location="form", type=int)


@send_record_ns.route("/send_record")
@send_record_ns.doc(description="Send a single customer record.")
class SendRecord(Resource):
    @send_record_ns.expect(
        send_record_ns.model(
            "Record",
            {
                "name": fields.String(required=True),
                "age": fields.Integer(required=True),
                "cookie": fields.String(required=True),
                "banner_id": fields.Integer(required=True),
                "min_age": fields.Integer,
                "max_age": fields.Integer,
            },
        ),
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
            rec = Record(
                **{
                    k: v
                    for k, v in data.items()
                    if k in {"name", "age", "cookie", "banner_id"}
                }
            )
        except TypeError:
            log.error(
                "/send_record: Failed to transform received data to Record object."
            )
            log.error(f"/send_record: {data}.")
            return {"message": "Failed to process data."}, HTTPStatus.BAD_REQUEST
        msg = f"Record {rec.cookie} did not pass the validation, ignored."
        if rec.validate(data.get("min_age"), data.get("max_age")):
            log.debug(f"/send_record: Sending {rec.cookie} to ShowAds API.")
            send_record(rec)
            msg = f"Record {rec.cookie} sent to ShowAPI."
        return {"message": msg}, HTTPStatus.ACCEPTED


@send_record_ns.route("/send_record/bulk")
@send_record_ns.doc(description="Send a bulk of records using a CSV file.")
class SendBulk(Resource):
    @send_record_ns.doc(parser=file_parser)
    @send_record_ns.response(
        code=HTTPStatus.BAD_REQUEST,
        description="File is missing.",
        model=fields.String,
        envelope="message",
    )
    @send_record_ns.response(
        code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        description="Received file is not supported.",
        model=fields.String,
        envelope="message",
    )
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
        if not upload_file:
            return {"message": "CSV file required."}, HTTPStatus.BAD_REQUEST
        if not allowed_file_extension(upload_file.filename):
            return {
                "message": "Unsupported file format. Only CSV files are accepted."
            }, HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        buffer = parse_file(upload_file, args.get("min_age"), args.get("max_age"))
        nof_recs = send_data(buffer)
        return {"sent": nof_recs}, HTTPStatus.ACCEPTED
