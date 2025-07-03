# test_from_gevu/src/services/github_api.py
import requests
from src.config.config import GITHUB_TOKEN
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_org_repos(org_name: str) -> List[Dict[str, Any]]:
    """
    Lista todos os repositórios da organização especificada.
    Lida com paginação e rate limiting.
    """
    if not org_name:
        logger.error("Nome da organização não fornecido para a API do GitHub.")
        return []

    repos = []
    page = 1
    per_page = 100
    while True:
        url = f"{BASE_URL}/orgs/{org_name}/repos?per_page={per_page}&page={page}"
        logger.info(f"Buscando repositórios: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            repos.extend(data)

            remaining_calls = int(response.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            if remaining_calls == 0:
                sleep_duration = max(0, reset_time - time.time()) + 1
                logger.warning(f"Limite de requisições atingido. Aguardando {sleep_duration:.0f} segundos.")
                time.sleep(sleep_duration)

            page += 1
        except requests.exceptions.Timeout:
            logger.error("Requisição ao GitHub excedeu o tempo limite.")
            break
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                logger.error("Erro de autenticação: Verifique seu GITHUB_TOKEN.")
            elif response.status_code == 404:
                logger.error(f"Organização '{org_name}' não encontrada ou sem acesso. Verifique o nome da organização e as permissões do token.")
            else:
                logger.error(f"Erro ao buscar repositórios do GitHub: {e}")
            break
    return repos

def extract_repo_info(repo_json: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai informações relevantes de um objeto JSON de repositório do GitHub."""
    return {
        "github_id": repo_json["id"],
        "nome": repo_json["name"],
        "visibilidade": "público" if not repo_json["private"] else "privado",
        "data_criacao": repo_json["created_at"],
        "data_ultima_atualizacao": repo_json["updated_at"],
        "estrelas": repo_json["stargazers_count"],
        "forks": repo_json["forks_count"],
        "url": repo_json["html_url"],
    }