from docxtpl import DocxTemplate
import os
import time

from dados_evento.maio26 import evento
from data.get_data import carregar_expositores, preparar_expositor

print("INICIANDO GERAÇÃO DE CONTRATOS")

start_time = time.perf_counter()

df = carregar_expositores()

total_contratos = len(df)

count = 0

PAGAMENTO_PARCELADO = "10% DE ENTRADA E O RESTANTE PARCELADO EM ATÉ 6X SEM JUROS"

if not os.path.exists("contratos"):
        os.makedirs("contratos")

for _, row in df.iterrows():

    if row["Forma de pagamento"] == PAGAMENTO_PARCELADO:
        doc = DocxTemplate("template/template_parcelado.docx")
    else:
         doc = DocxTemplate("template/template_avista.docx")

    expositor = preparar_expositor(row)

    context = {**evento, **expositor}

    doc.render(context)

    nome_arquivo = f"contrato_{row['Nome fantasia']}.docx"

    caminho = os.path.join("contratos/", nome_arquivo)
    doc.save(caminho)
    count +=1
    print(f"[{count},{total_contratos}] CONTRATOS GERADOS")

end_time = time.perf_counter()

tempo_total = end_time - start_time

tempo_medio = tempo_total / total_contratos

print("Contratos gerados!",
      f"\n[{count},{total_contratos}] CONTRATOS GERADOS",
      f"\nTempo Gasto: {round(tempo_total)} Segundos",
      f"\nMÉDIA DE {round(tempo_medio,3)} SEGUNDOS POR CONTRATO")