import io
import os

from flask import Blueprint, send_file, jsonify
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

blueprint = Blueprint("api", __name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")


@blueprint.route("/invoice", methods=["GET"])
def invoice():
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("invoice/index.html")
        html_str = template.render()

        pdf_buffer = io.BytesIO()  # alternative to temp file
        HTML(string=html_str).write_pdf(pdf_buffer, stylesheets=[os.path.join(TEMPLATE_DIR, "invoice", "style.css")])
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name="document.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
