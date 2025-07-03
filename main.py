
import os
import logging
from typing import Optional, List, Dict, Any

# ATENÇÃO: Caminhos dos imports e uso das instâncias dos modelos foram atualizados
from src.models.model import project_model, repository_model
from src.services.github_api import get_org_repos, extract_repo_info
from src.services.project_importer import import_projects_from_csv, import_projects_from_json
# Novo import para o carregador de regras
from src.services.rule_loader import load_assignment_rules_from_yaml
from src.config.config import PROJECTS_CSV_PATH, PROJECTS_JSON_PATH, \
    DEFAULT_PROJECT_NAME, setup_logging

logger = logging.getLogger(__name__)

# Variável global para armazenar as regras de atribuição
# Ela será populada pela função do rule_loader
assignment_rules: Optional[List[Dict[str, Any]]] = None


def assign_repo_to_project(repo_name: str) -> Optional[int]:
    """
    Função de lógica para atribuir um repositório a um projeto com base em regras carregadas.
    """
    global assignment_rules  # Usamos a variável global

    if assignment_rules is None or not assignment_rules:  # Verifica se as regras foram carregadas
        logger.warning(
            "Nenhuma regra de atribuição de projeto carregada ou as regras estão vazias. Usando o projeto padrão.")
        return project_model.get_id_by_name(DEFAULT_PROJECT_NAME)

    for rule in assignment_rules:
        project_name_from_rule = rule.get("project_name")
        keywords = rule.get("keywords", [])

        if not project_name_from_rule or not isinstance(keywords, list):
            logger.warning(f"Regra de atribuição inválida: {rule}. Ignorando.")
            continue

        for keyword in keywords:
            if keyword.lower() in repo_name.lower():
                project_id = project_model.get_id_by_name(project_name_from_rule)
                if project_id:
                    logger.debug(f"Repositório '{repo_name}' associado a '{project_name_from_rule}'.")
                    return project_id
                else:
                    logger.warning(
                        f"Projeto '{project_name_from_rule}' da regra '{rule}' não encontrado no banco de dados. Verifique o arquivo de projetos. Tentando a próxima regra se houver.")
                    break  # Sai do loop de keywords para esta regra, tenta a próxima regra

    logger.warning(
        f"Repositório '{repo_name}' não pôde ser associado a um projeto conhecido por nenhuma regra. Usando o projeto padrão.")
    return project_model.get_id_by_name(DEFAULT_PROJECT_NAME)


def main():
    logger.info("Iniciando monitoramento de repositórios GitHub...")

    project_model.create_table()
    repository_model.create_table()

    # 1. Carregar regras de atribuição usando o serviço dedicado
    logger.info("\nCarregando regras de atribuição de projetos...")
    global assignment_rules
    assignment_rules = load_assignment_rules_from_yaml()
    if assignment_rules is None:  # Se retornar None, houve uma falha
        logger.error("Falha ao carregar as regras de atribuição. A aplicação não pode continuar.")
        return
    if not assignment_rules:  # Se retornar uma lista vazia, mas sem erro fatal
        logger.warning(
            "O arquivo de regras de atribuição foi carregado, mas não contém nenhuma regra. Repositórios serão associados ao projeto padrão.")

    # 2. Cadastrar/Importar projetos e obter o nome da organização
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
        project_model.insert(DEFAULT_PROJECT_NAME, "Repositórios que não foram associados a um projeto específico.")

    # 3. Obter repositórios do GitHub para a organização carregada
    logger.info(f"\nColetando repositórios do GitHub para a organização '{github_organization_name}'...")
    github_repos = get_org_repos(github_organization_name)

    if not github_repos:
        logger.warning("Nenhum repositório encontrado ou erro ao acessar a API do GitHub. Encerrando.")
        return

    logger.info(f"Encontrados {len(github_repos)} repositórios.")

    # 4. Processar e armazenar repositórios
    logger.info("\nProcessando e armazenando repositórios...")
    for repo_json in github_repos:
        repo_data = extract_repo_info(repo_json)

        projeto_id = assign_repo_to_project(repo_data["nome"])

        if projeto_id:
            repo_data["projeto_id"] = projeto_id
            repository_model.insert_or_update(repo_data)
        else:
            logger.critical(
                f"Repositório '{repo_data['nome']}' não pôde ser associado a nenhum projeto (nem mesmo o padrão). Isso é um erro inesperado e indica um problema na lógica de atribuição ou no projeto padrão.")

    logger.info("\nMonitoramento de repositórios concluído.")


if __name__ == "__main__":
    setup_logging()
    main()