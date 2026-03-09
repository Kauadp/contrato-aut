import os
import sys
from dotenv import load_dotenv

def resource_path(relative_path):
    """ Obtém o caminho absoluto para recursos, funciona em dev e no PyInstaller """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path(".env"))

AUTENTIQUE_TOKEN = os.getenv("AUTENTIQUE_TOKEN")
EXCEL_URL = os.getenv("EXCEL_URL")

if not AUTENTIQUE_TOKEN:
    raise ValueError("AUTENTIQUE_TOKEN não encontrado no arquivo .env")

if not EXCEL_URL:
    raise ValueError("EXCEL_URL não encontrado no arquivo .env")