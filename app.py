import streamlit as st
from src.processamento_demandas import fluxo_busca_demandas, ler_demandas
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

URL_TRIZY = os.getenv('URL_TRIZY', '')
TOKEN = os.getenv('TOKEN', '')
PATH_SAVE_DEMANDAS = Path(os.getenv('PATH_SAVE_DEMANDAS', ''))
NAME_FILE_OUTPUT = 'demandas.csv'
PATH_TO_SAVE_DEMANDAS = PATH_SAVE_DEMANDAS / NAME_FILE_OUTPUT

PATH_SAVE_DEMANDAS.mkdir(exist_ok=True)

# def get_data_atualizacao():
#     return datetime.now().strftime('%d/%m/%Y, %H:%M:%S')

st.title('Gerenciador de Demandas', text_alignment='center')

try:
    if st.sidebar.button('Atualizar Demandas', type='primary'):

        ler_demandas.clear()
        fluxo_busca_demandas.clear() 
        fluxo_busca_demandas(URL_TRIZY, TOKEN, PATH_TO_SAVE_DEMANDAS)
        st.success('Demandas atualizadas')
        st.write()
except Exception as e:
    st.error(f'Erro ao acessa API{e}')

try:
    df = ler_demandas(PATH_TO_SAVE_DEMANDAS)

    if not df.empty:
        loja_selecionada = st.sidebar.selectbox(
            'Nome Loja',
            sorted(df['nome_loja'].unique()),
            index=None,
            placeholder="Selecione o nome da loja...",
        )

        status_demanda = st.sidebar.selectbox(
            'Status Demanda',
            sorted(df['status_demanda'].unique()),
            index=None,
            placeholder="Selecione o status da demanda...",
        )

        if not loja_selecionada and not status_demanda:
            st.dataframe(df, hide_index=True)
        elif loja_selecionada and not status_demanda:
            filtros = ((df['nome_loja'] == loja_selecionada))
            df_filtered = df.loc[filtros]
            st.table(df_filtered)
        elif not loja_selecionada and status_demanda:
            filtros = ((df['status_demanda'] == status_demanda))
            df_filtered = df.loc[filtros]
            st.table(df_filtered)
        elif loja_selecionada and status_demanda:
            filtros = ((df['nome_loja'] == loja_selecionada) & (df['status_demanda'] == status_demanda))
            df_filtered = df.loc[filtros]
            st.table(df_filtered)
        else:
            st.warning('Nenhuma tabela a mostra!')
    else:
        st.warning('Nenhum dado disponível.')

except Exception as e:
    st.error(f'Erro ao visualizar demandas: {e}')