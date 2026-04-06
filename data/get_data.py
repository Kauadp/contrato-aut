import pandas as pd
from num2words import num2words
import requests
from io import BytesIO
import re

def carregar_expositores(url):
    """
    Carrega a planilha de expositores e faz limpeza básica.
    
    Args:
        url: URL da planilha Excel a carregar (obrigatório)
    
    Returns:
        DataFrame com expositores filtrados
        
    Raises:
        ValueError: Se URL não for fornecida
        RequestException: Se houver erro ao baixar a planilha
    """
    if not url:
        raise ValueError(
            "URL da planilha não foi fornecida. "
            "Use EventoService.obter_url_planilha() para obter a URL do evento."
        )

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
    df["Contrato Status"] = df["Contrato Status"].str.strip().str.capitalize()
    df = df[df["Contrato Status"] == "Aguardando"]

    print(f"[DEBUG] Colunas encontradas na planilha: {list(df.columns)}")
    print(f"[DEBUG] Coluna 'Comissionado' existe? {'Comissionado' in df.columns}")

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
    Converte valores no formato brasileiro para float.
    Aceita:
    - R$ 1.234,56
    - 1.234,56
    - 1234,56
    - 1234.56
    - "", NaN
    """

    if valor == "" or pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    if isinstance(valor, str):
        # Remove R$, espaços e qualquer coisa que não seja número, vírgula, ponto ou sinal
        valor = re.sub(r"[^\d,.\-]", "", valor)

        # Se tiver vírgula, assume formato brasileiro
        if "," in valor:
            valor = valor.replace(".", "")
            valor = valor.replace(",", ".")

    return float(valor)


def formatar_real(valor):
    """
    Formata valores para R$.
    """
     
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def extrair_percentual_comissionado(valor_comissionado):
    """
    Extrai percentual no formato "X%" e retorna decimal.
    Exemplos:
    - "5%" -> 0.05
    - "12,5%" -> 0.125
    - "", NA, NULO -> None
    """
    if valor_comissionado is None or pd.isna(valor_comissionado):
        return None

    texto = str(valor_comissionado).strip().upper()
    if texto in {"", "NA", "N/A", "NULO", "NULL", "-"}:
        return None

    # Caso venha como número puro (ex: 0.1, 10, 10.0)
    if "%" not in texto:
        numero_limpo = texto.replace(",", ".")
        try:
            numero = float(numero_limpo)
            # Regra:
            # - <= 1: assume decimal (0.1 -> 10%)
            # - > 1: assume percentual inteiro (10 -> 10%)
            if numero <= 1:
                return numero
            return numero / 100
        except ValueError:
            return None

    match = re.search(r"(\d+(?:[.,]\d+)?)\s*%", texto)
    if not match:
        return None

    percentual = match.group(1).replace(",", ".")
    return float(percentual) / 100


def calcular_valor_total_comissionado(valor_minimo_garantido, percentual_comissionado):
    """
    Calcula o valor total de faturamento necessário para cobrir a comissão.
    Fórmula: mínimo_garantido / percentual
    """
    if not percentual_comissionado:
        return None

    return valor_minimo_garantido / percentual_comissionado


def preparar_expositor(row):

    valor = limpar_valor(row["Valor"])
    comissionado_raw = row.get("Comissionado", "")
    percentual_comissionado = extrair_percentual_comissionado(comissionado_raw)
    valor_total_comissionado = calcular_valor_total_comissionado(valor, percentual_comissionado)
    nome_fantasia = limpar_texto(row.get("Nome Fantasia", "SEM NOME"))

    print(
        f"[DEBUG] {nome_fantasia} | Comissionado bruto='{comissionado_raw}' "
        f"| percentual_decimal={percentual_comissionado} "
        f"| valor_minimo={valor} "
        f"| valor_total_comissionado={valor_total_comissionado}"
    )

    entrada = valor_entrada(valor)
    restante = valor_restante(valor)

    expositor = {

        #### STAND ####

        "EXPOSITOR": limpar_texto(row["Razão social"]),
        "NOMEFANTASIAEXPOSITOR": limpar_texto(row["Nome Fantasia"]),
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
        "PERCENTUALCOMISSAO": (
            f"{percentual_comissionado * 100:g}%"
            if percentual_comissionado is not None else ""
        ),
        "PERCENTUALCOMISSAODECIMAL": percentual_comissionado,
        "VALORTOTALCOMISSIONADO": (
            formatar_real(valor_total_comissionado)
            if valor_total_comissionado is not None else ""
        ),
        "VALORTOTALCOMISSIONADONUMERICO": valor_total_comissionado,
        "EHCOMISSIONADO": percentual_comissionado is not None,

        "VALOREXTENSO": num2words(valor, lang="pt_BR") + " reais",
        "VALORTOTALCOMISSIONADOEXTENSO": (
            num2words(valor_total_comissionado, lang="pt_BR") + " reais"
            if valor_total_comissionado is not None else ""
        ),

        #### FOOD ####

        "DOCUMENTOREPRESENTENTAEXPOSITOR": limpar_texto(row["Nome Fantasia"]),
        "DOCUMENTOEXPOSITOR": limpar_texto(row["CPF (TITULAR CNPJ)"]),
        "RAZAOEXPOSITOR2": limpar_texto(row["Razão social"]),
        "DOCUMENTOEXPOSITOR2": limpar_texto(row["CPF (TITULAR CNPJ)"])

    }

    return expositor