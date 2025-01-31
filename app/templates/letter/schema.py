import os
from marshmallow import fields, Schema

from app.config import BASEDIR


class LetterSchema(Schema):
    recipient_name = fields.String(required=True)
    body = fields.String(required=True)
    author_name = fields.String(required=True)


schema = LetterSchema()

additional_data = {
    "stylesheet_url": f"file://{os.path.join(BASEDIR, "templates", "letter", "stylesheet-with-custom-name.css")}",
    "logo_url": f"file://{os.path.join(BASEDIR, "templates", "letter", "img", "logo-couleurs.png")}",
}
