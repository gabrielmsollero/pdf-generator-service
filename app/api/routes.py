import os

from flask import Blueprint, jsonify

blueprint = Blueprint("api", __name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")


@blueprint.route("/invoice", methods=["GET"])
def invoice():
    return jsonify({"message": "hello world!"})
