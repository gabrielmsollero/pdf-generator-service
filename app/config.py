import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))

    TEMPLATES_DIR = os.path.join(BASEDIR, "templates")
    TEMPLATE_FILE_NAME = "index.html"
    STYLESHEETS_FILE_NAME = "style.css"
