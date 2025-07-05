
import sqlite3
import logging
from typing import Optional
from src.config.config import DATABASE_NAME
from src.models.model import DatabaseManager

logger = logging.getLogger(__name__)

class ProjectRepository:
    """Gerencia as operações CRUD para a tabela Projetos."""

    def __init__(self):
        self.db_manager = DatabaseManager(DATABASE_NAME)

    def insert_project(self, nome: str, descricao: Optional[str] = None) -> Optional[int]:
        """
        Insere um novo projeto no banco de dados.
        Retorna o ID do projeto inserido ou existente.
        """
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO Projetos (nome, descricao) VALUES (?, ?)", (nome, descricao))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Projeto '{nome}' inserido com sucesso (ID: {cursor.lastrowid}).")
                    return cursor.lastrowid
                else:
                    logger.info(f"Projeto '{nome}' já existe.")
                    return self.get_project_id_by_name(nome)
            except sqlite3.Error as e:
                logger.error(f"Erro ao inserir projeto '{nome}': {e}")
                return None

    def get_project_id_by_name(self, nome: str) -> Optional[int]:
        """Retorna o ID de um projeto pelo nome."""
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM Projetos WHERE nome = ?", (nome,))
                result = cursor.fetchone()
                return result["id"] if result else None
            except sqlite3.Error as e:
                logger.error(f"Erro ao buscar ID do projeto '{nome}': {e}")
                return None

project_repository = ProjectRepository()