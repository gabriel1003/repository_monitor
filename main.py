import os
import logging
from typing import Optional, List, Dict, Any
import yaml

from src.models.model import SchemaManager
from src.repositories.project_repository import project_repository
from src.repositories.github_repository import github_repository
from src.services.github_api import get_org_repos, extract_repo_info
from src.services.project_importer import import_projects_from_csv, import_projects_from_json
from src.services.rule_loader import load_assignment_rules_from_yaml
from src.config.config import PROJECTS_CSV_PATH, PROJECTS_JSON_PATH, \
    DEFAULT_PROJECT_NAME, setup_logging, DATABASE_NAME

logger = logging.getLogger(__name__)

assignment_rules: Optional[List[Dict[str, Any]]] = None


def assign_repo_to_project(repo_name: str) -> Optional[int]:
    """
    Função de lógica para atribuir um repositório a um projeto com base em regras carregadas.
    """
    global assignment_rules

    if assignment_rules is None or not assignment_rules:
        logger.warning(
            "Nenhuma regra de atribuição de projeto carregada ou as regras estão vazias. Usando o projeto padrão.")
        # Chama o método do repositório de projetos
        return project_repository.get_project_id_by_name(DEFAULT_PROJECT_NAME)

    for rule in assignment_rules:
        project_name_from_rule = rule.get("project_name")
        keywords = rule.get("keywords", [])

        if not project_name_from_rule or not isinstance(keywords, list):
            logger.warning(f"Regra de atribuição inválida: {rule}. Ignorando.")
            continue

        for keyword in keywords:
            if keyword.lower() in repo_name.lower():

                project_id = project_repository.get_project_id_by_name(project_name_from_rule)
                if project_id:
                    logger.debug(f"Repositório '{repo_name}' associado a '{project_name_from_rule}'.")
                    return project_id
                else:
                    logger.warning(
                        f"Projeto '{project_name_from_rule}' da regra '{rule}' não encontrado no banco de dados. Verifique o arquivo de projetos. Tentando a próxima regra se houver.")
                    break

    logger.warning(
        f"Repositório '{repo_name}' não pôde ser associado a um projeto conhecido por nenhuma regra. Usando o projeto padrão.")

    return project_repository.get_project_id_by_name(DEFAULT_PROJECT_NAME)


def main():
    logger.info("Iniciando monitoramento de repositórios GitHub...")

    schema_manager = SchemaManager(DATABASE_NAME)
    schema_manager.create_all_tables()  # Cria todas as tabelas

    logger.info("\nCarregando regras de atribuição de projetos...")
    global assignment_rules
    assignment_rules = load_assignment_rules_from_yaml()
    if assignment_rules is None:
        logger.error("Falha ao carregar as regras de atribuição. A aplicação não pode continuar.")
        return
    if not assignment_rules:
        logger.warning(
            "O arquivo de regras de atribuição foi carregado, mas não contém nenhuma regra. Repositórios serão associados ao projeto padrão.")

    logger.info("\nImportando projetos e nome da organização...")
    github_organization_name = None
    if os.path.exists(PROJECTS_CSV_PATH):
        github_organization_name = import_projects_from_csv()
    elif os.path.exists(PROJECTS_JSON_PATH):
        github_organization_name = import_projects_from_json()
    else:
        logger.error(
            "Nenhum arquivo de projetos CSV ou JSON encontrado. A aplicação não pode continuar sem o nome da organização e projetos.")
        return

    if not github_organization_name:
        logger.error(
            "Nome da organização do GitHub não foi encontrado nos arquivos de projetos. A aplicação não pode continuar.")
        return
    else:
        logger.info(f"Organização GitHub a ser monitorada: {github_organization_name}")

        project_repository.insert_project(DEFAULT_PROJECT_NAME,
                                          "Repositórios que não foram associados a um projeto específico.")

    logger.info(f"\nColetando repositórios do GitHub para a organização '{github_organization_name}'...")
    github_repos = get_org_repos(github_organization_name)

    if not github_repos:
        logger.warning("Nenhum repositório encontrado ou erro ao acessar a API do GitHub. Encerrando.")
        return

    logger.info(f"Encontrados {len(github_repos)} repositórios.")

    logger.info("\nProcessando e armazenando repositórios...")
    for repo_json in github_repos:
        repo_data = extract_repo_info(repo_json)

        projeto_id = assign_repo_to_project(repo_data["nome"])

        if projeto_id:
            repo_data["projeto_id"] = projeto_id
            github_repository.insert_or_update_repository(repo_data)
        else:
            logger.critical(
                f"Repositório '{repo_data['nome']}' não pôde ser associado a nenhum projeto (nem mesmo o padrão). Isso é um erro inesperado e indica um problema na lógica de atribuição ou no projeto padrão.")

    logger.info("\nMonitoramento de repositórios concluído.")


if __name__ == "__main__":
    setup_logging()
    main()