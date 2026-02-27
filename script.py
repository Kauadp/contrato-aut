import pandas as pd
from docxtpl import DocxTemplate
import os
import num2words
import locale
from datetime import datetime

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

hoje = datetime.now()

data_extenso = hoje.strftime("%A, %d de %B de %Y")

# 1) carregar planilha
df = pd.read_csv("expositor/expositor.csv")

# 2) dados fixos do evento
evento = {
    "DESCRICAOEVENTO": "EXAGERADO MAIO PAVILHÃO 2026",
    "CPFREPRESENTANTEORGANIZADOR": "013.714.186-67",
    "ENDERECOREPRESENTANTEORGANIZADOR": "Braulina Baptista Lopes, 150, Edíficio, Rosario de Fátima, SERRA/ES. CEP: 29161-121",
    "PERIODOEVENTO": "De 06 de Maio de 2026 à 10 de Maio de 2026",
    "HORARIOEVENTO": "Das 10:00 as 22:00",
    "LOCALEVENTO": "PAVILHÃO DE CARAPINA, SN, PAVILHÃO DE CARAPINA OU PAR. ESTADUAL AGROPECUÁR, CARAPINA, SERRA/ES. CEP: 29161-064.",
    "ANTECEDENCIAENTREGAESPACO": "1",
    "REFERENCIALIBERACAO": "05/05/2026",
    "HORAINICIOLIBERACAO": "09:00",
    "HORATERMINOLIBERACAO": "18:00",
    "PENALIDADEIRREGULARIDADE": "R$ 1.000,00",
    "PENALIDADECONTRATACAOMENOR": "R$ 1.000,00",
    "PENALIDADERESCISAO": "R$ 1.000,00",
    "EXPOSITORDATALIMITEPAGAMENTO": "04/05/2026",
    "PRAZOENVIOLOGOMARCA": "04/05/2026",
    "PENALIDADEMARCA": "R$ 1.000,00",
    "PENALIDADEDESVIOFINALIDADE": "R$ 1.000,00",
    "PORCENTEGEMLIMITEESTOQUEMINIMO": "20%",
    "PORCENTAGEMINFRACAOLIMITEESTOQUEMINIMO": "30%",
    "PENALIDADEDANOSMINIMOS": "R$ 50,00",
    "PENALIDADEDANOSMAXIMOS": "R$ 5.000,00",
    "PENALIDADESUBLOCACAO": "R$ 5.000,00",
    "INFRACAODESCONTO": "R$ 1.000,00",
    "VALECOMPRA": "R$ 100,00",
    "PRAZOMAXIMOOCUPACAOESPACO": "8 horas",
    "PENALIDADEQUEBRACONTRATO": "R$ 2.000,00",
    "HORARIOEXPOSITOR": "09:30 horas",
    "PENALIDADEATRASOABERTURA": "R$ 100,00",
    "HORARIOABERTURA2": "10:00 horas",
    "HORARIOFECHAMENTO": "22:00 horas",
    "TOLERANCIAFECHAMENTO": "30 minutos",
    "MULTAATRASOFECHAMENTO": "R$ 100,00",
    "HORARIOLIMITEFECHAMENTO": "22:30",
    "DATAPAGAMENTOALUGALSTAND": "04/05/2026",
    "DATAENTRADA": "20/03/2025",
    "EXPOSITORDATALIMITEPAGAMENTO": "31/03/2026",
    "DATAEXTENSO": data_extenso,
    
}

# 3) loop para gerar contratos
for index, row in df.iterrows():

    # abrir template
    doc = DocxTemplate("template/template.docx")

    # dados do expositor
    expositor = {
        "EXPOSITOR": row["Razão social"],
        "NOMEFANTASIAEXPOSITOR": row["Nome fantasia"],
        "CNPJEXPOSITOR": row["CNPJ"],
        "INSCRICAOESTADUALEXPOSITOR": row["Inscrição Estadual"],
        "ENDERECOSEDEEXPOSITOR": row["Endereço comercial"],
        "FUNCAOCONTRATUALEXPOSITOR": "Proprietário",
        "RESPONSAVELCONTRATUALEXPOSITOR": row["Nome completo (Sócio proprietário)"],
        "CPFRESPONSAVELCONTRATUALEXPOSITOR": row["CPF (TITULAR CNPJ)"],
        "RGRESPONSALVELCONTRATUALEXPOSITOR": row["RG (TITULAR CNPJ)"],
        "LISTADEMARCAS": "A IMPLEMENTAR", # PLANILHA STAND
        "EXPOSITORAREASTAND": "A IMPLEMENTAR", # PLANILHA ESTAND
        "VALORTOTALALUGUELSTAND": "A IMPLEMENTAR", # METRAGEM X VALOR M2 PLANILHA STAND
        "VALOREXTENSO": "A IMPLEMENTAR", # UTILIZAR LIB NUM2WORD
        "ENTRADAVALOR": "A IMPLEMENTAR", # CALCULAR 10% DO VALOR TOTAL
        "VALORRESTANTE": "A IMPLEMENTAR", # CALCULAR 90% DO VALOR TOTAL
    }

    # juntar dados
    context = {**evento, **expositor}

    # preencher template
    doc.render(context)

    # nome do arquivo
    nome_arquivo = f"contrato_{row['Nome fantasia']}.docx"
    output_directory = "contratos/"

    full_nome = os.path.join(output_directory, nome_arquivo)

    # salvar contrato
    doc.save(full_nome)

print("Contratos gerados!")