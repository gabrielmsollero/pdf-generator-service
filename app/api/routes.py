import io
import json
import os
from importlib import import_module

from flask import Blueprint, current_app, jsonify, request, send_file
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from marshmallow import Schema, ValidationError
from weasyprint import HTML
from werkzeug.exceptions import HTTPException, InternalServerError

from app.config import build_time_logger, Config

blueprint = Blueprint("api", __name__)


def register_route_for_template(template_name: str):
    logger = build_time_logger
    logger.info(f"building route for template '{template_name}'")
    error_msg = None
    try:
        schema_module = import_module(f"app.templates.{template_name}.schema")
        schema: Schema = schema_module.schema
        if not isinstance(schema, Schema):
            raise TypeError(f"schema must be an instance of {Schema}, not {type(schema)}")

        env = Environment(loader=FileSystemLoader(os.path.join(Config.TEMPLATES_DIR, template_name)))
        template = env.get_template(Config.TEMPLATE_FILE_NAME)
    except ModuleNotFoundError:
        error_msg = (
            "could not find schema module for template. Make sure there is a schema.py file inside the template folder"
        )
    except AttributeError:
        error_msg = "could not find a variable named 'schema' inside the schema module"
    except TypeError as e:
        error_msg = str(e)
    except TemplateNotFound:
        error_msg = f"could not find a template file named '{Config.TEMPLATE_FILE_NAME}' inside the template folder"
    except Exception as e:
        logger.exception("unexpected error while building route:")
        error_msg = str(e)
    finally:
        if error_msg:
            logger.error(
                f"error while building route: {error_msg}. This template will be skipped and won't be available."
            )
            return

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
    logger.info("route built successfully")


for folder_name in os.listdir(Config.TEMPLATES_DIR):
    register_route_for_template(folder_name)


@blueprint.app_errorhandler(HTTPException)
def handle_http_exception(e: HTTPException):
    current_app.logger.info(f"http exception: {str(e)}")
    return jsonify({"error": e.description}), e.code
