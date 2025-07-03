# test_from_gevu/src/config/config.py

import os
from dotenv import load_dotenv
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.join(current_dir, '..', '..', '..')

load_dotenv(os.path.join(project_root_dir, '.env'))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_NAME = os.path.join(project_root_dir, "repos_monitor.db")
PROJECTS_CSV_PATH = os.path.join(project_root_dir, "data", "projetos.csv")
PROJECTS_JSON_PATH = os.path.join(project_root_dir, "data", "projetos.json")

# --- Novo caminho para o arquivo YAML de regras de atribuição ---
PROJECT_ASSIGNMENT_RULES_PATH = os.path.join(project_root_dir, "data", "project_assignment_rules.yaml")

# --- Configuração de Logging ---
LOG_FILE = os.path.join(project_root_dir, "app.log")
LOG_LEVEL = logging.INFO

# --- Configuração para Lógica de Atribuição de Projetos (Removido daqui, será carregado do YAML) ---
# PROJECT_ASSIGNMENT_RULES foi removido
DEFAULT_PROJECT_NAME = "Projeto Diversos"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN não configurado nas variáveis de ambiente. Verifique o arquivo .env.")

# Configuração inicial do logging
def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

setup_logging()

logging.info("Configurações carregadas com sucesso.")