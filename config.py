import os
from dotenv import load_dotenv

load_dotenv()

AUTENTIQUE_TOKEN = os.getenv("AUTENTIQUE_TOKEN")
EXCEL_URL = os.getenv("EXCEL_URL")

if not AUTENTIQUE_TOKEN:
    raise ValueError("AUTENTIQUE_TOKEN não encontrado no arquivo .env")

if not EXCEL_URL:
    raise ValueError("EXCEL_URL não encontrado no arquivo .env")