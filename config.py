import os
from dotenv import load_dotenv
import json

load_dotenv()  # Load environment variables from .env

# Base folder where data is stored
DATA_FOLDER = os.getenv("FOLDER", "/tmp")
HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("PORT", 4000)
SSL_KEYFILE = os.getenv("SSL_KEYFILE")
SSL_CERTFILE = os.getenv("SSL_CERTFILE")

# POS-related environment variables
LOGIN_URL = os.getenv("LOGIN_URL")
FILTER_URL = os.getenv("FILTER_URL")
EXPORT_URL = os.getenv("EXPORT_URL")
DOWNLOAD_URL = os.getenv("DOWNLOAD_URL")
LOGOUT_URL = os.getenv("LOGOUT_URL")

# Authentication
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Email settings
FROM_EMAIL = os.getenv("FROM_EMAIL")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_USER = os.getenv("SMTP_USER")
REPORTING_EMAIL = os.getenv("REPORTING_EMAIL")
DAILY_EMAIL = os.getenv("DAILY_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", 587)

# Additional
SHOP_NAME = os.getenv("SHOP_NAME", "Demo")
B1_API_KEY = os.getenv("B1_API_KEY", "demo")
PREFIX_SUPPLIER_MAP = json.loads(os.getenv("PREFIX_SUPPLIER_MAP"))