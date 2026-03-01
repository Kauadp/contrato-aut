import pandas as pd
from num2words import num2words

def carregar_expositores(caminho_csv):
    """
    Carrega a planilha de expositores e faz limpeza básica.
    """

    df = pd.read_csv(caminho_csv)

    # remover espaços extras nas colunas
    df.columns = df.columns.str.strip()

    # substituir valores faltantes
    df = df.fillna("")

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