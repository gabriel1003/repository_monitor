# test_from_gevu/src/models/model.py

import sqlite3
from typing import Optional, Dict, Any, List
from src.config.config import DATABASE_NAME
import logging

# Configura o logger para o módulo models
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerencia a conexão com o banco de dados SQLite."""
    def __init__(self, db_name: str):
        self.db_name = db_name

    def __enter__(self):
        """Abre a conexão ao entrar no bloco 'with'."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
            return self.conn
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados '{self.db_name}': {e}")
            raise # Re-lança a exceção para que o chamador possa lidar com ela

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do bloco 'with'."""
        if self.conn:
            self.conn.close()

class ProjectModel:
    """Modelo para interagir com a tabela Projetos."""

    def __init__(self):
        self.db_manager = DatabaseManager(DATABASE_NAME)
        self.create_table()

    def create_table(self):
        """Cria a tabela Projetos se não existir."""
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Projetos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT UNIQUE NOT NULL,
                        descricao TEXT
                    );
                """)
                conn.commit()
                logger.info("Tabela 'Projetos' criada ou já existente.")
            except sqlite3.Error as e:
                logger.error(f"Erro ao criar tabela 'Projetos': {e}")
                raise

    def insert(self, nome: str, descricao: Optional[str] = None) -> Optional[int]:
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
                    return self.get_id_by_name(nome)
            except sqlite3.Error as e:
                logger.error(f"Erro ao inserir projeto '{nome}': {e}")
                return None

    def get_id_by_name(self, nome: str) -> Optional[int]:
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

class RepositoryModel:
    """Modelo para interagir com a tabela Repositorios."""

    def __init__(self):
        self.db_manager = DatabaseManager(DATABASE_NAME)
        self.create_table()

    def create_table(self):
        """Cria a tabela Repositorios se não existir."""
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Repositorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        github_id INTEGER UNIQUE NOT NULL, -- ID do GitHub para evitar duplicatas por API
                        nome TEXT NOT NULL,
                        visibilidade TEXT NOT NULL,
                        data_criacao TEXT NOT NULL,
                        data_ultima_atualizacao TEXT NOT NULL,
                        estrelas INTEGER,
                        forks INTEGER,
                        url TEXT NOT NULL UNIQUE,
                        projeto_id INTEGER,
                        FOREIGN KEY (projeto_id) REFERENCES Projetos(id)
                    );
                """)
                conn.commit()
                logger.info("Tabela 'Repositorios' criada ou já existente.")
            except sqlite3.Error as e:
                logger.error(f"Erro ao criar tabela 'Repositorios': {e}")
                raise

    def insert_or_update(self, repo_data: Dict[str, Any]) -> bool:
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

# Instâncias dos modelos para serem usadas por outros módulos
project_model = ProjectModel()
repository_model = RepositoryModel()

# As funções antigas podem ser removidas ou substituídas por métodos das classes
# Para compatibilidade temporária (se outros arquivos ainda as chamarem diretamente):
# def create_tables():
#     project_model.create_table()
#     repository_model.create_table()

# def insert_project(nome, descricao=None):
#     return project_model.insert(nome, descricao)

# def get_project_id_by_name(nome):
#     return project_model.get_id_by_name(nome)

# def insert_or_update_repository(repo_data):
#     return repository_model.insert_or_update(repo_data)