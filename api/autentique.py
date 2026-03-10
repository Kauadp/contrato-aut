import requests
import os
from config import AUTENTIQUE_TOKEN
import json

def enviar_para_autentique(
    caminho_pdf,
    nome_documento,
    nome_signatario,
    email_signatario
    #telefone_signatario
):

    url = "https://api.autentique.com.br/v2/graphql"

    headers = {
        "Authorization": f"Bearer {AUTENTIQUE_TOKEN}",
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
                    "name": nome_signatario,
                    "email": email_signatario,
                    #"phone": telefone_signatario,
                    "action": "SIGN",
                    "order": 2
                },

                {
                    "name": "VICTOR DE CASTRO PEREIRA",
                    "email": "gabrielly.concecio@alfaiatariadeideias.com.br",
                    "action": "SIGN",
                    "order": 1
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