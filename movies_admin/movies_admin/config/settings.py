import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

DEBUG = os.environ.get("DEBUG", False) == "True"

include(
    "components/installed_apps.py",
    "components/middleware.py",
    "components/database.py",
    "components/templates.py",
    "components/auth_password_validators.py",
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split()

INTERNAL_IPS = os.environ.get("INTERNAL_IPS", "").split()

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = "/vol/web/static"
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOCALE_PATHS = ["movies/locale"]

FILE_API_UVICORN_HOST_DIRECT = os.environ.get("FILE_API_UVICORN_HOST_DIRECT", "localhost")
FILE_API_UVICORN_HOST = os.environ.get("FILE_API_UVICORN_HOST", "localhost")
FILE_API_UVICORN_PORT = os.environ.get("FILE_API_UVICORN_PORT", "8080")
