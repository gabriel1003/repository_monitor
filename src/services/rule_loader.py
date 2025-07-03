
import os
import yaml
import logging
# --- ADICIONE ESTA LINHA ---
from typing import Optional, List, Dict, Any
# --- FIM DA LINHA ADICIONADA ---

from src.config.config import PROJECT_ASSIGNMENT_RULES_PATH

logger = logging.getLogger(__name__)


def load_assignment_rules_from_yaml() -> Optional[List[Dict[str, Any]]]:
    """
    Carrega as regras de atribuição de projetos de um arquivo YAML.
    Retorna uma lista de dicionários de regras ou None em caso de falha.
    """
    try:
        if not os.path.exists(PROJECT_ASSIGNMENT_RULES_PATH):
            logger.error(f"Arquivo de regras de atribuição '{PROJECT_ASSIGNMENT_RULES_PATH}' não encontrado.")
            return None

        with open(PROJECT_ASSIGNMENT_RULES_PATH, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            if data and 'rules' in data and isinstance(data['rules'], list):
                logger.info(f"Regras de atribuição carregadas com sucesso de '{PROJECT_ASSIGNMENT_RULES_PATH}'.")
                return data['rules']
            else:
                logger.error(
                    f"Formato inválido no arquivo de regras YAML '{PROJECT_ASSIGNMENT_RULES_PATH}'. Esperado 'rules' como uma lista.")
                return None
    except yaml.YAMLError as e:
        logger.error(f"Erro ao analisar o arquivo YAML '{PROJECT_ASSIGNMENT_RULES_PATH}': {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar regras de atribuição: {e}")
        return None