
import sqlite3
import logging
from typing import Dict, Any
from src.config.config import DATABASE_NAME
from src.models.model import DatabaseManager

logger = logging.getLogger(__name__)

class GitHubRepositoryRepository:
    """Gerencia as operações CRUD para a tabela Repositorios."""

    def __init__(self):
        self.db_manager = DatabaseManager(DATABASE_NAME)

    def insert_or_update_repository(self, repo_data: Dict[str, Any]) -> bool:
        """
        Insere ou atualiza um repositório no banco de dados.
        Recebe um dicionário com os dados do repositório, incluindo 'projeto_id'.
        """
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM Repositorios WHERE github_id = ?", (repo_data["github_id"],))
                existing_repo = cursor.fetchone()

                if existing_repo:
                    cursor.execute("""
                        UPDATE Repositorios SET
                            nome = ?, visibilidade = ?, data_criacao = ?,
                            data_ultima_atualizacao = ?, estrelas = ?, forks = ?,
                            url = ?, projeto_id = ?
                        WHERE github_id = ?
                    """, (
                        repo_data["nome"], repo_data["visibilidade"], repo_data["data_criacao"],
                        repo_data["data_ultima_atualizacao"], repo_data["estrelas"], repo_data["forks"],
                        repo_data["url"], repo_data["projeto_id"], repo_data["github_id"]
                    ))
                    logger.info(f"Repositório '{repo_data['nome']}' atualizado.")
                else:
                    cursor.execute("""
                        INSERT INTO Repositorios (
                            github_id, nome, visibilidade, data_criacao,
                            data_ultima_atualizacao, estrelas, forks, url, projeto_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        repo_data["github_id"], repo_data["nome"], repo_data["visibilidade"],
                        repo_data["data_criacao"], repo_data["data_ultima_atualizacao"],
                        repo_data["estrelas"], repo_data["forks"], repo_data["url"], repo_data["projeto_id"]
                    ))
                    logger.info(f"Repositório '{repo_data['nome']}' inserido.")
                conn.commit()
                return True
            except sqlite3.Error as e:
                logger.error(f"Erro ao inserir/atualizar repositório '{repo_data.get('nome', 'N/A')}': {e}")
                return False

github_repository = GitHubRepositoryRepository()