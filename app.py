import streamlit as st
import pandas as pd
import plotly.express as px
from core.data_engine import AnalisadorAcoes
from core.database import RepositorioLogs

db = RepositorioLogs()

st.set_page_config(page_title='Dashboard Financeiro', layout='wide')

st.sidebar.markdown('## Parâmetros de Análise')
ativos_disponiveis = ['^BVSP', 'PETR4.SA', 'LREN3.SA', 'MGLU3.SA', 'VALE3.SA', 'ITUB4.SA']

ativos = st.sidebar.multiselect('Ações', ativos_disponiveis, default=['PETR4.SA'])
data_inicio = st.sidebar.date_input('Início', pd.to_datetime('2024-01-01'))
data_fim = st.sidebar.date_input('Fim', pd.to_datetime('today'))

st.sidebar.markdown('---')
st.sidebar.markdown('### Em Alta (Mais Buscados)')
ranking = db.obter_ativos_mais_buscados()

if ranking:
    for ativo, qtd in ranking:
        st.sidebar.text(f"📈 {ativo}: {qtd} buscas")
else:
    st.sidebar.caption("Nenhum histórico ainda.")

st.title('Análise Financeira 🇧🇷')

if not ativos:
    st.info('⬅️ Selecione as ações na barra lateral.')
else:
    analisador = AnalisadorAcoes(ativos, data_inicio, data_fim)
    
    with st.spinner("Conectando ao provedor de dados..."):
        dados = analisador.buscar_dados()
        kpis = analisador.calcular_metricas()

    if dados.empty:
        st.error('Ocorreu um erro de comunicação com a API ou não há dados.')
    else:
        db.registrar_busca(ativos)
        
        st.header('Métricas de Desempenho')
        colunas = st.columns(len(ativos))
        
        for idx, ativo in enumerate(ativos):
            with colunas[idx]:
                metricas = kpis[ativo]
                st.metric(
                    label=f'{ativo}',
                    value=f"R$ {metricas['ultimo_preco']:.2f}",
                    delta=f"{metricas['retorno_perc']:.2f}%",
                    delta_color='inverse' if metricas['retorno_perc'] < 0 else 'normal'
                )
                st.caption(f"Volatilidade: {metricas['volatilidade_anual']:.2f}%")