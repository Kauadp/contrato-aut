import requests
import os
import json
from dotenv import load_dotenv
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path(".env"))

# Fallback para compatibilidade (se AUTENTIQUE_TOKEN global existir)
AUTENTIQUE_TOKEN = os.getenv("AUTENTIQUE_TOKEN")

def enviar_para_autentique(
    caminho_pdf,
    nome_documento,
    nome_signatario,
    email_signatario,
    token_autentique=None
    #telefone_signatario
):
    """
    Envia um documento para a API Autentique para assinatura digital.
    
    Args:
        caminho_pdf: Caminho do arquivo PDF a ser enviado
        nome_documento: Nome do documento
        nome_signatario: Nome do signatário
        email_signatario: Email do signatário
        token_autentique: Token da Autentique (se None, usa token global de config.py)
    
    Returns:
        Resposta JSON da API Autentique
        
    Raises:
        ValueError: Se nenhum token for fornecido
    """
    
    # Usa token fornecido ou fallback para token global (compatibilidade)
    if token_autentique is None:
        token_autentique = AUTENTIQUE_TOKEN
    
    if not token_autentique:
        raise ValueError(
            "Token da Autentique não fornecido.\n"
            "Passe token_autentique como parâmetro ou configure AUTENTIQUE_TOKEN no .env"
        )

    url = "https://api.autentique.com.br/v2/graphql"

    headers = {
        "Authorization": f"Bearer {token_autentique}",
    }

    query = """
    mutation CreateDocument($file: Upload!, $document: DocumentInput!, $signers: [SignerInput!]!) {
      createDocument(file: $file, document: $document, signers: $signers) {
        id
        name
      }
    }
    """

    operations = {
        "query": query,
        "variables": {
            "file": None,
            "document": {
                "name": nome_documento
            },
            "signers": [

                {
                    "name": "VICTOR DE CASTRO PEREIRA",
                    "email": "gabrielly.concecio@alfaiatariadeideias.com.br",
                    "action": "SIGN"
                },

                {
                    "name": nome_signatario,
                    "email": email_signatario,
                    #"phone": telefone_signatario,
                    "action": "SIGN"
                }

            ]
        }
    }

    map_ = {
        "0": ["variables.file"]
    }

    with open(caminho_pdf, "rb") as f:
        files = {
            "operations": (None, json.dumps(operations), "application/json"),
            "map": (None, json.dumps(map_), "application/json"),
            "0": (nome_documento + ".pdf", f, "application/pdf")
        }

        response = requests.post(url, headers=headers, files=files)

    return response.json()