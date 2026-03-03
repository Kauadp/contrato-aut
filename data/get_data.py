import pandas as pd
from num2words import num2words
import requests
from io import BytesIO


def carregar_expositores(url = 'https://timealfaiataria-my.sharepoint.com/:x:/g/personal/ldr02_alfaiatariadeideias_com_br/IQAkbIGee1upR5u973Mlw3ZmAbLL4eDotl780N5o_-wgFHQ?e=aWswYS&download=1'):
    """
    Carrega a planilha de expositores e faz limpeza básica.
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    file = BytesIO(response.content)
    df = pd.read_excel(file, sheet_name="CONTRATOS")

    # remover espaços extras nas colunas
    df.columns = df.columns.str.strip()

    # substituir valores faltantes
    df = df.fillna("")

    # Filtro Inicial
    df = df[df["Tipo de STAND:"] == "STAND"]
    df = df[df["Contrato Status"] == "Aguardando"]

    return df


def limpar_texto(valor):
    """
    Remove espaços extras de textos.
    """

    if isinstance(valor, str):
        return valor.strip()

    return valor

def valor_entrada(valor):
    """
    Calcula 10% de entrada.
    """

    return .1 * valor


def valor_restante(valor):
    """
    Calcula 90% restantes.
    """

    return .9 * valor


def limpar_valor(valor):
    """
    Limpa valores numéricos.
    """

    if valor == "" or pd.isna(valor):
        return 0.0

    if isinstance(valor, str):
        valor = valor.replace(".", "").replace(",", ".")
    return float(valor)


def formatar_real(valor):
    """
    Formata valores para R$.
    """
     
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def preparar_expositor(row):

    valor = limpar_valor(row["Valor"])

    entrada = valor_entrada(valor)
    restante = valor_restante(valor)

    expositor = {
        "EXPOSITOR": limpar_texto(row["Razão social"]),
        "NOMEFANTASIAEXPOSITOR": limpar_texto(row["Nome fantasia"]),
        "CNPJEXPOSITOR": limpar_texto(row["CNPJ"]),
        "INSCRICAOESTADUALEXPOSITOR": limpar_texto(row["Inscrição Estadual"]),
        "ENDERECOSEDEEXPOSITOR": limpar_texto(row["Endereço comercial"]),
        "FUNCAOCONTRATUALEXPOSITOR": "Proprietário",
        "RESPONSAVELCONTRATUALEXPOSITOR": limpar_texto(row["Nome completo (Sócio proprietário)"]),
        "CPFRESPONSAVELCONTRATUALEXPOSITOR": limpar_texto(row["CPF (TITULAR CNPJ)"]),
        "RGRESPONSALVELCONTRATUALEXPOSITOR": limpar_texto(row["RG (TITULAR CNPJ)"]),
        "LISTADEMARCAS": limpar_texto(row["Marcas (que você levará para o evento)"]),

        "STANDNUMERO": limpar_texto(row["Stand"]),
        "EXPOSITORAREASTAND": row["Area"],

        "VALORTOTALALUGUELSTAND": formatar_real(valor),
        "ENTRADAVALOR": formatar_real(entrada),
        "VALORRESTANTE": formatar_real(restante),

        "VALOREXTENSO": num2words(valor, lang="pt_BR") + " reais",
    }

    return expositor