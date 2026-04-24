import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AnalisadorAcoes:
    def __init__(self, ativos: list, data_inicio, data_fim):
        self.ativos = ativos
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.dados_brutos = pd.DataFrame()
        
    def buscar_dados(self) -> pd.DataFrame:
        if not self.ativos:
            logging.warning("Tentativa de busca sem ativos selecionados.")
            return pd.DataFrame()
        try:
            logging.info(f"Iniciando integração na API para os ativos: {self.ativos}")
            self.dados_brutos = yf.download(self.ativos, start=self.data_inicio,
                                            end=self.data_fim, auto_adjust=True)
            logging.info("Busca concluida com sucesso.")
            return self.dados_brutos            
        except Exception as e:
            logging.error(f"Falha na integração com Yahoo Finance: {e}")
            return pd.DataFrame()
            
    def obter_dados_fechamento(self) -> pd.DataFrame:
        if self.dados_brutos.empty:
            return pd.DataFrame()
        
        fechamento = self.dados_brutos['Close'].copy()
        
        if isinstance(fechamento, pd.Series):
            return fechamento.to_frame(name=self.ativos[0])
        if len(self.ativos) == 1 and len(fechamento.columns) == 1:
            fechamento.columns = [self.ativos[0]]
        
        return fechamento
    
    def calcular_metricas(self) -> dict:
        fechamento = self.obter_dados_fechamento()
        if fechamento.empty:
            return {}

        metricas = {}
        retorno_acumulado = fechamento.iloc[-1] / fechamento.iloc[0] - 1
        volatilidade = fechamento.pct_change().std() * (252**0.5)
        
        for ativo in self.ativos:
            metricas[ativo] = {
                'ultimo_preco': fechamento[ativo].iloc[-1],
                'preco_inicial': fechamento[ativo].iloc[0],
                'retorno_perc': retorno_acumulado[ativo] * 100,
                'volatilidade_anual': volatilidade[ativo] * 100
            }
        return metricas