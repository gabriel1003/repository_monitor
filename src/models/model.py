
import sqlite3
import logging
from src.config.config import DATABASE_NAME

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerencia a conexão com o banco de dados SQLite."""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def __enter__(self):
        """Abre a conexão ao entrar no bloco 'with'."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            return self.conn
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados '{self.db_name}': {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do bloco 'with'."""
        if self.conn:
            self.conn.close()


class SchemaManager:
    """Gerencia a criação das tabelas no banco de dados."""

    def __init__(self, db_name: str):
        self.db_manager = DatabaseManager(db_name)

    def create_all_tables(self):
        """Cria todas as tabelas necessárias se não existirem."""
        with self.db_manager as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS Projetos
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   nome
                                   TEXT
                                   UNIQUE
                                   NOT
                                   NULL,
                                   descricao
                                   TEXT
                               );
                               """)
                logger.info("Tabela 'Projetos' criada ou já existente.")

                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS Repositorios
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   github_id
                                   INTEGER
                                   UNIQUE
                                   NOT
                                   NULL,
                                   nome
                                   TEXT
                                   NOT
                                   NULL,
                                   visibilidade
                                   TEXT
                                   NOT
                                   NULL,
                                   data_criacao
                                   TEXT
                                   NOT
                                   NULL,
                                   data_ultima_atualizacao
                                   TEXT
                                   NOT
                                   NULL,
                                   estrelas
                                   INTEGER,
                                   forks
                                   INTEGER,
                                   url
                                   TEXT
                                   NOT
                                   NULL
                                   UNIQUE,
                                   projeto_id
                                   INTEGER,
                                   FOREIGN
                                   KEY
                               (
                                   projeto_id
                               ) REFERENCES Projetos
                               (
                                   id
                               )
                                   );
                               """)
                conn.commit()
                logger.info("Tabela 'Repositorios' criada ou já existente.")
            except sqlite3.Error as e:
                logger.error(f"Erro ao criar tabelas: {e}")
                raise