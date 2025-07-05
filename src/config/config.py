

import os
from dotenv import load_dotenv
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.join(current_dir, '..', '..')

load_dotenv(os.path.join(project_root_dir, '.env'))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DATABASE_NAME = os.path.join(project_root_dir, "data", "repos_monitor.db")
PROJECTS_CSV_PATH = os.path.join(project_root_dir, "data", "projetos.csv")
PROJECTS_JSON_PATH = os.path.join(project_root_dir, "data", "projetos.json")

PROJECT_ASSIGNMENT_RULES_PATH = os.path.join(project_root_dir, "data", "project_assignment_rules.yaml")

LOG_FILE = os.path.join(project_root_dir, "app.log")
LOG_LEVEL = logging.INFO

DEFAULT_PROJECT_NAME = "Projeto Diversos"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN não configurado nas variáveis de ambiente. Verifique o arquivo .env.")

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