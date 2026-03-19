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

# Variáveis de fallback (compatibilidade com código antigo)
# Preferir usar EventoService.obter_token_autentique() e obter_url_planilha()
AUTENTIQUE_TOKEN = os.getenv("AUTENTIQUE_TOKEN")  # Fallback para ES se existir
EXCEL_URL = os.getenv("EXCEL_URL")  # Fallback para ES se existir

# Nota: Validações específicas por evento agora são feitas em EventoService