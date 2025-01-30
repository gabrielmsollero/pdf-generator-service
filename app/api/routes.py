import json
import io
import os

from flask import current_app, Blueprint, jsonify, request, send_file
from jinja2 import Environment, FileSystemLoader
from marshmallow import Schema, fields, ValidationError
from weasyprint import HTML
from werkzeug.exceptions import HTTPException

blueprint = Blueprint("api", __name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")


class InvoiceItemSchema(Schema):
    description = fields.String(required=True)
    unit_price = fields.Float(required=True)
    quantity = fields.Integer(required=True)


class InvoiceSchema(Schema):
    invoice_number = fields.String(required=True)
    account_number = fields.String(required=True)
    emission_date = fields.Date(required=True, format="%Y/%m/%d")
    due_by = fields.Date(required=True, format="%Y/%m/%d")
    total_due = fields.Float(required=True)
    items = fields.List(fields.Nested(InvoiceItemSchema), required=True)


invoice_schema = InvoiceSchema()


@blueprint.route("/invoice", methods=["POST"])
def invoice():
    logger = current_app.logger
    try:
        logger.info(f"receiving request for template 'invoice'")
        logger.info(json.dumps(request.json, indent=2))
        try:
            data = invoice_schema.load(request.json)
        except ValidationError as err:
            logger.info("validation error while processing request body")
            logger.info(json.dumps(err.messages, indent=2))
            return jsonify({"error": err.messages}), 400

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("invoice/index.html")
        logger.info("rendering document")
        html_str = template.render(**data)

        logger.info("writing to PDF")
        pdf_buffer = io.BytesIO()  # alternative to temp file
        HTML(string=html_str).write_pdf(pdf_buffer, stylesheets=[os.path.join(TEMPLATE_DIR, "invoice", "style.css")])
        pdf_buffer.seek(0)

        logger.info("sending response")
        return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name="document.pdf")
    except HTTPException as e:
        logger.info(f"http exception while processing request: {e.description}")
        return jsonify({"error": e.description}), e.code
    except Exception as e:
        logger.exception(f"unexpected error while processing request:")
        return jsonify({"error": str(e)}), 500
