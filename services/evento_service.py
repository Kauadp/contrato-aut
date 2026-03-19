"""
Serviço para gerenciar configurações e dados de eventos.
Abstrai a lógica de obter configs, URLs de planilhas e dados específicos do evento.
"""

import os
import sys
from config.eventos import obter_evento, EventoConfig
from dotenv import load_dotenv


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Carrega .env uma única vez
load_dotenv(resource_path(".env"))


class EventoService:
    """
    Serviço centralizado para gerenciar configurações e dados de eventos.
    """

    def __init__(self, sigla_evento: str = None):
        """
        Inicializa o serviço com um evento específico.
        Se sigla_evento é None, usa o evento padrão (ES).
        """
        self.config = obter_evento(sigla_evento)
        self._dados_evento = None

    def obter_config(self) -> EventoConfig:
        """Retorna a configuração do evento atual."""
        return self.config

    def obter_sigla(self) -> str:
        """Retorna a sigla do evento (ex: 'ES', 'RJ')."""
        return self.config.sigla

    def obter_url_planilha(self) -> str:
        """
        Obtém a URL da planilha do evento.
        Prioridade: variável de ambiente específica do evento > variável antiga (ES only) > erro
        
        Raises:
            ValueError: Se a URL não for encontrada
        """
        sigla = self.config.sigla
        env_var = self.config.excel_url_env
        
        url = os.getenv(env_var)
        
        if not url and sigla == "ES":
            # Fallback para compatibilidade com .env antigo
            url = os.getenv("EXCEL_URL")
        
        if not url:
            raise ValueError(
                f"URL da planilha não encontrada para evento {sigla}.\n"
                f"Configure a variável de ambiente '{env_var}' no arquivo .env\n"
                f"Exemplo:\n{env_var}=https://seu-sharepoint.com/..."
            )
        
        return url

    def obter_token_autentique(self) -> str:
        """
        Obtém o token da API Autentique para o evento.
        Prioridade: variável de ambiente específica do evento > variável antiga (ES only) > erro
        
        Raises:
            ValueError: Se o token não for encontrado
        """
        sigla = self.config.sigla
        env_var = self.config.autentique_token_env
        
        token = os.getenv(env_var)
        
        if not token and sigla == "ES":
            # Fallback para compatibilidade com .env antigo
            token = os.getenv("AUTENTIQUE_TOKEN")
        
        if not token:
            raise ValueError(
                f"Token da Autentique não encontrado para evento {sigla}.\n"
                f"Configure a variável de ambiente '{env_var}' no arquivo .env\n"
                f"Exemplo:\n{env_var}=seu_token_aqui"
            )
        
        return token

    def obter_dados_evento(self):
        """
        Carrega e cacheia os dados específicos do evento.
        Ex: evento_stand, evento_food (contexto para templates).
        """
        if self._dados_evento is None:
            self._dados_evento = self._carregar_dados_evento()
        return self._dados_evento

    def _carregar_dados_evento(self):
        """
        Importa dinamicamente o módulo de dados do evento.
        Ex: para 'ES', importa dados_evento.es
        """
        sigla = self.config.sigla.lower()

        try:
            modulo = __import__(f"dados_evento.{sigla}", fromlist=[""])
            return modulo
        except ImportError as e:
            raise ImportError(
                f"Não foi possível carregar dados para o evento {self.config.sigla}. "
                f"Verifique se o arquivo dados_evento/{sigla}.py existe. "
                f"Erro: {e}"
            )

    def obter_dados_stand(self):
        """Retorna os dados específicos para tipo STAND."""
        dados = self.obter_dados_evento()
        if not hasattr(dados, "evento_stand"):
            raise AttributeError(
                f"evento_stand não encontrado em dados_evento/{self.config.sigla.lower()}.py"
            )
        return dados.evento_stand

    def obter_dados_food(self):
        """Retorna os dados específicos para tipo FOOD."""
        dados = self.obter_dados_evento()
        if not hasattr(dados, "evento_food"):
            raise AttributeError(
                f"evento_food não encontrado em dados_evento/{self.config.sigla.lower()}.py"
            )
        return dados.evento_food

    def verificar_templates_disponiveis(self) -> bool:
        """Verifica se os templates do evento estão disponíveis."""
        return self.config.templates_disponiveis
