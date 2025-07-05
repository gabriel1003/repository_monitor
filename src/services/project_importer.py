import csv
import json
import os
import logging
from typing import Optional

from src.repositories.project_repository import project_repository
from src.config.config import PROJECTS_CSV_PATH, PROJECTS_JSON_PATH

logger = logging.getLogger(__name__)


def import_projects_from_csv() -> Optional[str]:
    """Importa projetos de um arquivo CSV e retorna o nome da organização."""
    organization_name = None
    projects_to_insert = []
    try:
        if not os.path.exists(PROJECTS_CSV_PATH):
            logger.error(f"Arquivo CSV de projetos '{PROJECTS_CSV_PATH}' não encontrado.")
            return None

        with open(PROJECTS_CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if i == 0:
                    organization_name = row.get("organizacao_github")
                    if not organization_name:
                        logger.warning("Campo 'organizacao_github' não encontrado na primeira linha do CSV.")

                nome = row.get("nome")
                descricao = row.get("descricao")

                if nome:
                    projects_to_insert.append({"nome": nome, "descricao": descricao})
                else:
                    logger.warning(f"Linha ignorada no CSV por falta de 'nome': {row}")

            for project in projects_to_insert:
                project_repository.insert_project(project["nome"],
                                                  project["descricao"])  # Chama o método do repositório

    except Exception as e:
        logger.error(f"Erro ao importar projetos do CSV: {e}")

    return organization_name


def import_projects_from_json() -> Optional[str]:
    """Importa projetos de um arquivo JSON e retorna o nome da organização."""
    organization_name = None
    try:
        if not os.path.exists(PROJECTS_JSON_PATH):
            logger.error(f"Arquivo JSON de projetos '{PROJECTS_JSON_PATH}' não encontrado.")
            return None

        with open(PROJECTS_JSON_PATH, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list) and data:
                first_item = data[0]
                organization_name = first_item.get("organizacao_github")
                if not organization_name:
                    logger.warning("Campo 'organizacao_github' não encontrado no primeiro objeto do JSON.")

                for item in data:
                    nome = item.get("nome")
                    descricao = item.get("descricao")
                    if nome:
                        project_repository.insert_project(nome, descricao)  # Chama o método do repositório
                    else:
                        logger.warning(f"Item ignorado no JSON por falta de 'nome': {item}")
            else:
                logger.error("Formato JSON inválido: Esperado uma lista de objetos não vazia.")
    except json.JSONDecodeError:
        logger.error(f"Arquivo '{PROJECTS_JSON_PATH}' não é um JSON válido.")
    except Exception as e:
        logger.error(f"Erro ao importar projetos do JSON: {e}")

    return organization_name