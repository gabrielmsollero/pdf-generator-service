import io
import json
import logging
import os
from importlib import import_module

from flask import current_app, Blueprint, jsonify, request, send_file
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from marshmallow import Schema, ValidationError
from weasyprint import HTML
from werkzeug.exceptions import HTTPException, InternalServerError

from app.config import Config

blueprint = Blueprint("api", __name__)


def register_route_for_template(template_name: str):
    try:
        schema: Schema = import_module(f"app.templates.{template_name}.schema").schema
        if not isinstance(schema, Schema):
            raise TypeError(f"schema must be an instance of {Schema}, not {type(schema)}")
    except (ModuleNotFoundError, AttributeError, TypeError):
        logging.error(
            f"error while loading schema for template '{template_name}'. Make sure there is a schema.py "
            f"file containing a schema variable of type {Schema} inside the template folder."
        )

    env = Environment(loader=FileSystemLoader(os.path.join(Config.TEMPLATES_DIR, template_name)))
    try:
        template = env.get_template(Config.TEMPLATE_FILE_NAME)
    except TemplateNotFound:
        logging.error(
            f"error while loading HTML file for template '{template_name}'. "
            f"Make sure there is an {Config.TEMPLATE_FILE_NAME} file inside the template folder."
        )

    def route_handler():
        logger = current_app.logger
        try:
            logger.info(f"receiving request for template '{template_name}': {json.dumps(request.json, indent=2)}")
            try:
                data = schema.load(request.json)
            except ValidationError as err:
                logger.info(f"validation error while processing request body: {json.dumps(err.messages, indent=2)}")
                return jsonify({"error": err.messages}), 400

            logger.info("rendering document")
            html_str = template.render(**data)

            logger.info("writing to PDF")
            pdf_buffer = io.BytesIO()  # alternative to temp file
            css_file_path = os.path.join(Config.TEMPLATES_DIR, template_name, Config.STYLESHEETS_FILE_NAME)
            HTML(string=html_str).write_pdf(
                pdf_buffer, stylesheets=[css_file_path] if os.path.exists(css_file_path) else []
            )
            pdf_buffer.seek(0)

            logger.info("sending response")
            return send_file(
                pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name=f"{template_name}.pdf"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.exception(f"unexpected error while processing request:")
            raise InternalServerError(str(e))

    blueprint.add_url_rule(rule=template_name, endpoint=template_name, view_func=route_handler, methods=["POST"])


for folder_name in os.listdir(Config.TEMPLATES_DIR):
    register_route_for_template(folder_name)


@blueprint.app_errorhandler(HTTPException)
def handle_http_exception(e: HTTPException):
    current_app.logger.info(f"http exception: {str(e)}")
    return jsonify({"error": e.description}), e.code
