from docxtpl import DocxTemplate
import os
import time
from docx2pdf import convert

from dados_evento.maio26 import evento_stand, evento_food
from data.get_data import carregar_expositores, preparar_expositor
from api.autentique import enviar_para_autentique
from api.brasil_api import validar_cnpj
import base64
import json
import unicodedata
import re

def normalizar_nome(nome):
    if not nome:
        return ""

    # remove acentos
    nome = ''.join(
        c for c in unicodedata.normalize('NFD', nome)
        if unicodedata.category(c) != 'Mn'
    )

    # remove caracteres especiais
    nome = re.sub(r'[^A-Za-z\s]', '', nome)

    return nome.upper().strip()

def nomes_batem(nome_planilha, lista_socios):

    nome_planilha = normalizar_nome(nome_planilha)
    palavras_planilha = set(nome_planilha.split())

    for socio in lista_socios:
        socio_norm = normalizar_nome(socio)
        palavras_socio = set(socio_norm.split())

        # Interseção de palavras
        intersecao = palavras_planilha.intersection(palavras_socio)

        # Regra: pelo menos 2 palavras iguais
        if len(intersecao) >= 2:
            return True

    return False

def converter_docx_para_pdf(caminho_docx):
    convert(caminho_docx, keep_active=True)
    return caminho_docx.replace(".docx", ".pdf")

print("INICIANDO GERAÇÃO DE CONTRATOS")

start_time = time.perf_counter()

df = carregar_expositores()

total_contratos = len(df)

count = 0

cnpjs_invalidos = []
cnpjs_nao_encontrados = []

PAGAMENTO_PARCELADO = "10% DE ENTRADA E O RESTANTE PARCELADO EM ATÉ 6X SEM JUROS"
PAGAMENTO_AVISTA = "PIX COM 5% DE DESCONTO"

if not os.path.exists("contratos"):
        os.makedirs("contratos")

for _, row in df.iterrows():

    expositor = preparar_expositor(row)

    tipo = row["Tipo de STAND:"]
    pagamento = row["Forma de pagamento"]

    print(f"Gerando contrato para: {row['Nome Fantasia']}\n")

    ativo, socios, status = validar_cnpj(row["CNPJ"])

    if status == 400:
        cnpjs_invalidos.append(row["Nome Fantasia"])
        print("CNPJ inválido — pulando contrato\n")
        continue

    if status == 404:
        cnpjs_nao_encontrados.append(row["Nome Fantasia"])

    if status not in [200, 404]:
        print("Erro ao consultar API\n")
        continue

    if not ativo:
        print("CNPJ não está ativo\n")
        continue

    if tipo == "STAND":
        context = {**evento_stand, **expositor}

        if pagamento == PAGAMENTO_PARCELADO:
            doc = DocxTemplate("template/template_parcelado.docx")
        else:
            doc = DocxTemplate("template/template_avista.docx")

    elif tipo == "FOOD":
        context = {**evento_food, **expositor}

        if pagamento == PAGAMENTO_PARCELADO:
            doc = DocxTemplate("template/template_food_parcelado.docx")
        else:
            doc = DocxTemplate("template/template_food_avista.docx")

    else:
        print(f"Tipo inválido: {tipo}")
        continue

    doc.render(context)

    nome_arquivo = f"contrato_{row['Nome Fantasia']}.docx"

    caminho = os.path.join("contratos/", nome_arquivo)
    doc.save(caminho)

    caminho_pdf = converter_docx_para_pdf(caminho)

    nome_documento = nome_arquivo.replace(".docx", "")

    resposta = enviar_para_autentique(
        caminho_pdf,
        nome_documento=nome_documento,
        nome_signatario=expositor["RESPONSAVELCONTRATUALEXPOSITOR"],
        email_signatario=row["E-mail (Sócio proprietário)"]
        #telefone_signatario=row["Telefone (Sócio proprietário)"]
    )

    if "errors" in resposta:
        print("ERRO AO ENVIAR:", resposta)
        continue
    else: print("CONTRATO POSTADO")

    print(json.dumps(resposta, indent=2))

    document_id = resposta["data"]["createDocument"]["id"]
    print("ID:", document_id)

    count +=1
    print(f"[{count},{total_contratos}] CONTRATOS GERADOS")

end_time = time.perf_counter()

tempo_total = end_time - start_time

tempo_medio = tempo_total / total_contratos

print("\n==============================")
print("CNPJs inválidos na planilha:")
for nome in cnpjs_invalidos:
    print("-", nome)

print("\nCNPJs não encontrados na Receita:")
for nome in cnpjs_nao_encontrados:
    print("-", nome)

print("Contratos gerados!",
      f"\n[{count},{total_contratos}] CONTRATOS GERADOS",
      f"\nTempo Gasto: {round(tempo_total)} Segundos",
      f"\nMÉDIA DE {round(tempo_medio,3)} SEGUNDOS POR CONTRATO")