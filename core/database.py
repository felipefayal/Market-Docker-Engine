import os
import sqlite3
import logging
from datetime import datetime

class RepositorioLogs:
    def __init__(self, db_diretorio="data", db_nome="dados_financeiros.db"):
        self.diretorio = db_diretorio
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)
            
        self.db_path = os.path.join(self.diretorio, db_nome)
        self._criar_tabela()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _criar_tabela(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS buscas_ativos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ativo TEXT NOT NULL,
                    data_busca DATETIME NOT NULL
                )
            ''')
            conn.commit() 

    def registrar_busca(self, ativos: list):
        try:
            with self._conectar() as conn:
                cursor = conn.cursor()
                agora = datetime.now()
                
                registros = [(ativo, agora) for ativo in ativos]
                
                cursor.executemany('''
                    INSERT INTO buscas_ativos (ativo, data_busca) 
                    VALUES (?, ?)
                ''', registros)
                logging.info(f"Log gravado com sucesso para: {ativos}")
        except Exception as e:
            logging.error(f"Erro ao salvar log no banco de dados: {e}")

    def obter_ativos_mais_buscados(self, limite=5):
        try:
            with self._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ativo, COUNT(*) as total 
                    FROM buscas_ativos 
                    GROUP BY ativo 
                    ORDER BY total DESC 
                    LIMIT ?
                ''', (limite,))
                return cursor.fetchall() 
        except Exception as e:
            logging.error(f"Erro ao buscar ranking: {e}")
            return []