from docxtpl import DocxTemplate
import os
import time
from docx2pdf import convert
import sys
import json
import unicodedata
import re

from data.get_data import carregar_expositores, preparar_expositor
from api.autentique import enviar_para_autentique
from api.brasil_api import validar_cnpj
from services.evento_service import EventoService
from services.template_service import TemplateService

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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

def extrair_email(email_raw):

    if not email_raw:
        return None

    email_raw = str(email_raw).strip()

    # pega todos emails válidos da string
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(regex, email_raw)

    if emails:
        return emails[0]  # pega só o primeiro
    else:
        return None

def iniciar_processamento(sigla_evento: str = None):
    """
    Inicia o processamento de geração de contratos para um evento específico.
    
    Args:
        sigla_evento: Sigla do evento (ex: 'ES', 'RJ'). Se None, usa o padrão (ES).
    
    Raises:
        ValueError: Se evento não existir ou credenciais não forem encontradas
    """
    print(f"INICIANDO GERAÇÃO DE CONTRATOS")

    # Inicializa serviços
    evento_service = EventoService(sigla_evento)
    template_service = TemplateService(evento_service.obter_sigla())

    config_evento = evento_service.obter_config()
    sigla_evento = config_evento.sigla.upper()
    print(f"Evento: {config_evento.nome}\n")

    # Verifica se templates estão disponíveis
    if not evento_service.verificar_templates_disponiveis():
        print(f"⚠️  AVISO: Templates para o evento {config_evento.sigla} ainda não foram criados.")
        print(f"Por favor, crie os templates e ajuste a configuração em config/eventos.py")
        return

    # Obtém credenciais do evento
    try:
        url_planilha = evento_service.obter_url_planilha()
        token_autentique = evento_service.obter_token_autentique()
    except ValueError as e:
        print(f"❌ ERRO DE CONFIGURAÇÃO:\n{e}")
        return

    start_time = time.perf_counter()

    # Carrega expositores usando a URL correta do evento
    df = carregar_expositores(url=url_planilha)

    total_contratos = len(df)

    count = 0

    cnpjs_invalidos = []
    cnpjs_nao_encontrados = []
    emails_invalidos = []

    if not os.path.exists("contratos"):
            os.makedirs("contratos")

    # Obtém dados contextuais do evento (evento_stand, evento_food)
    dados_evento = evento_service.obter_dados_evento()

    for _, row in df.iterrows():

        expositor = preparar_expositor(row)

        # Para RJ, a coluna "Tipo de STAND:" pode não existir, então assume "STAND"
        # Para ES, usa o valor da coluna
        tipo = row.get("Tipo de STAND:", "STAND")
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

        # Validar tipo
        tipos_validos = evento_service.obter_config().tipos_stand
        if tipo not in tipos_validos:
            print(f"Tipo inválido: {tipo}")
            continue

        # Obter dados contextuais do tipo
        if tipo == "STAND":
            dados_tipo = evento_service.obter_dados_stand()
        else:  # FOOD
            dados_tipo = evento_service.obter_dados_food()

        context = {**dados_tipo, **expositor}

        comissionado_habilitado_evento = sigla_evento in {"RJ", "SP"}
        contrato_comissionado = (
            comissionado_habilitado_evento
            and tipo == "STAND"
            and expositor.get("EHCOMISSIONADO", False)
        )

        # Selecionar template usando o serviço
        try:
            caminho_template = template_service.obter_caminho_template(
                tipo,
                pagamento,
                comissionado=contrato_comissionado
            )
            doc = DocxTemplate(caminho_template)
        except FileNotFoundError as e:
            print(f"ERRO: {e}\n")
            continue

        doc.render(context)

        nome_arquivo = f"contrato_{row['Nome Fantasia']}.docx"

        caminho = os.path.join("contratos/", nome_arquivo)
        doc.save(caminho)

        caminho_pdf = converter_docx_para_pdf(caminho)

        nome_documento = nome_arquivo.replace(".docx", "")

        email = extrair_email(row["E-mail (Sócio proprietário)"])

        if not email:
            emails_invalidos.append(row["Nome Fantasia"])
            print("Email inválido ou não encontrado — pulando envio para Autentique\n")
            continue

        #resposta = enviar_para_autentique(
        #    caminho_pdf,
        #    nome_documento=nome_documento,
        #    nome_signatario=expositor["RESPONSAVELCONTRATUALEXPOSITOR"],
        #    email_signatario=email,
        #    token_autentique=token_autentique
            #telefone_signatario=row["Telefone (Sócio proprietário)"]
        #)

       # if "errors" in resposta:
       #     print("ERRO AO ENVIAR:", resposta)
       #     continue
       # else: print("CONTRATO POSTADO")

        #print(json.dumps(resposta, indent=2))

        #document_id = resposta["data"]["createDocument"]["id"]
        #print("ID:", document_id)

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

    print("\n==============================")
    print("Emails inválidos na planilha:")
    for nome in emails_invalidos:
        print("-", nome)

    print("Contratos gerados!",
          f"\n[{count},{total_contratos}] CONTRATOS GERADOS",
          f"\nTempo Gasto: {round(tempo_total)} Segundos",
          f"\nMÉDIA DE {round(tempo_medio,3)} SEGUNDOS POR CONTRATO")

if __name__ == "__main__":
    iniciar_processamento()