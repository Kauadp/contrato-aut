"""
Serviço para gerenciar seleção e carregamento de templates.
Encapsula a lógica de localizar templates baseado em evento, tipo e forma de pagamento.
"""

import os
import sys
from pathlib import Path


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TemplateService:
    """
    Serviço para gerenciar templates de contrato.
    Define a convenção de nomenclatura e localiza templates.
    """

    # Convenção: template_[tipo_prefix][pagamento].docx
    # Tipo: STAND -> "" (vazio), FOOD -> "food_"
    # Pagamento: parcelado | avista
    TIPO_STAND = ""           # template_parcelado.docx
    TIPO_FOOD = "food_"        # template_food_parcelado.docx

    PAGAMENTO_PARCELADO = "parcelado"
    PAGAMENTO_AVISTA = "avista"

    def __init__(self, sigla_evento: str, caminho_templates: str = "template"):
        """
        Inicializa o serviço de templates.
        
        Args:
            sigla_evento: Sigla do evento (ex: 'ES', 'RJ')
            caminho_templates: Caminho da pasta com templates (padrão: 'template')
        """
        self.sigla_evento = sigla_evento
        self.caminho_templates = resource_path(caminho_templates)

    def obter_caminho_template(
        self, tipo: str, forma_pagamento: str
    ) -> str:
        """
        Retorna o caminho completo do template.
        
        Args:
            tipo: Tipo de stand ('STAND' ou 'FOOD')
            forma_pagamento: Forma de pagamento (string completa)
        
        Returns:
            Caminho absoluto do template (.docx)
        
        Raises:
            FileNotFoundError: Se o template não existir
            ValueError: Se o template estiver configurado como não disponível
        """
        tipo_prefix = self._normalizar_tipo(tipo)
        pagamento_norm = self._normalizar_pagamento(forma_pagamento)

        # Convenção: template_[tipo_prefix][pagamento]_[sigla_evento].docx
        # STAND + parcelado + ES -> template_parcelado_es.docx
        # FOOD + parcelado + RJ -> template_food_parcelado_rj.docx
        nome_template = f"template_{tipo_prefix}{pagamento_norm}_{self.sigla_evento.lower()}.docx"
        caminho_completo = os.path.join(self.caminho_templates, nome_template)

        if not os.path.exists(caminho_completo):
            raise FileNotFoundError(
                f"[{self.sigla_evento}] Template não encontrado: {nome_template}\n"
                f"Caminho esperado: {caminho_completo}\n"
                f"Verifique se o arquivo existe em {self.caminho_templates}/ ou se o evento tem templates registrados."
            )

        return caminho_completo

    def _normalizar_tipo(self, tipo: str) -> str:
        """
        Normaliza o tipo de stand para a convenção do template.
        'STAND' -> '' (vazio, sem prefixo)
        'FOOD' -> 'food_'
        Convenção existente: template_parcelado.docx vs template_food_parcelado.docx
        """
        tipo_map = {
            "STAND": "",           # template_parcelado.docx
            "FOOD": "food_",       # template_food_parcelado.docx
        }

        tipo_upper = tipo.upper()
        if tipo_upper not in tipo_map:
            raise ValueError(
                f"Tipo de stand inválido: '{tipo}'. "
                f"Valores válidos: {', '.join(tipo_map.keys())}"
            )

        return tipo_map[tipo_upper]

    def _normalizar_pagamento(self, forma_pagamento: str) -> str:
        """
        Normaliza a forma de pagamento para a convenção do template.
        Se contém 'PARCELADO' (case-insensitive) -> 'parcelado'
        Caso contrário -> 'avista'
        """
        if "PARCELADO" in forma_pagamento.upper():
            return self.PAGAMENTO_PARCELADO
        else:
            return self.PAGAMENTO_AVISTA

    def verificar_template_existe(self, tipo: str, forma_pagamento: str) -> bool:
        """
        Verifica se um template existe sem lançar exceção.
        Útil para validações prévias.
        """
        try:
            self.obter_caminho_template(tipo, forma_pagamento)
            return True
        except (FileNotFoundError, ValueError):
            return False

    def listar_templates(self) -> list:
        """
        Lista todos os templates disponíveis para o evento.
        """
        if not os.path.exists(self.caminho_templates):
            return []

        templates = []
        for arquivo in os.listdir(self.caminho_templates):
            if arquivo.startswith("template_") and arquivo.endswith(".docx"):
                templates.append(arquivo)

        return sorted(templates)
