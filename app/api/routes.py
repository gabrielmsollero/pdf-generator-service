import io
import json
import os
from datetime import date

from flask import Blueprint, jsonify, send_file
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

blueprint = Blueprint("api", __name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")


@blueprint.route("/invoice", methods=["GET"])
def invoice():
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template("invoice/index.html")
        data = json.loads(
            """
        {
            "invoice_number": "12345",
            "account_number": "123456789012",
            "total_due": 5000.00,
            "items": [
                {
                "description": "Website design",
                "unit_price": 34.2,
                "quantity": 100
                },
                {
                "description": "Website development",
                "unit_price": 45.5,
                "quantity": 99
                },
                {
                "description": "Website integration",
                "unit_price": 62.2,
                "quantity": 89
                }
            ]
        }
        """
        )
        html_str = template.render(**data, emission_date=date(2024, 11, 30), due_by=date(2024, 12, 1))

        pdf_buffer = io.BytesIO()  # alternative to temp file
        HTML(string=html_str).write_pdf(pdf_buffer, stylesheets=[os.path.join(TEMPLATE_DIR, "invoice", "style.css")])
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=True, download_name="document.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
