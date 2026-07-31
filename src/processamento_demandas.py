import requests
import pandas as pd
import numpy as np
import os
from pathlib import Path
import streamlit as st


def buscar_demandas(token: str, page: str) -> tuple:
    url = 'https://api.trizy.com.br/cargo/demanda'

    params = {
        'page': page,
        'startDate': '',
        'endDate': '',
        'searchText': ''
    }

    headers = {
        'authorization': f'Bearer {token}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        'accept': 'application/json, text/plain, */*'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.status_code, response.json()
    else:
        return response.status_code, {}


def carregar_demandas(lista_pagina_demandas: list[dict]) -> pd.DataFrame:
    lista_demandas = []

    for dados_demandas in lista_pagina_demandas:
        for demanda in dados_demandas:
            json_dados_demandas = {}
            json_dados_demandas['nome_loja'] = demanda['unidade']['nomeFantasia']
            json_dados_demandas['demanda'] = str(demanda['identificador'])
            json_dados_demandas['status_demanda'] = demanda['status']['status']
            json_dados_demandas['data_sugerida'] = demanda['dataSugeridaEntrega']
            json_dados_demandas['id_agendamento'] = demanda['agendamentoId'] if demanda['agendamentoId'] else np.nan
            json_dados_demandas['data_efetiva'] = demanda['dataEfetivaEntrega'] if demanda['dataEfetivaEntrega'] else np.nan

            lista_demandas.append(json_dados_demandas)

    df_demandas = pd.DataFrame.from_records(data=[[value for value in demanda.values()] for demanda in lista_demandas], columns=['nome_loja', 'demanda', 'status_demanda', 'data_sugerida', 'id_agendamento', 'data_efetiva'])
    df_demandas['data_sugerida'] = pd.to_datetime(df_demandas['data_sugerida'], errors='coerce')
    df_demandas['data_efetiva'] = pd.to_datetime(df_demandas['data_efetiva'], errors='coerce')

    return df_demandas


def salvar_demandas(df: pd.DataFrame, path: str | Path) -> None:
    df.to_csv(path, index=False)
    # if os.path.exists(path):
    #     df.to_csv(path, index=False, mode='a', header=False)
    # else:
    #     df.to_csv(path, index=False)


@st.cache_data
def fluxo_busca_demandas(token: str, path: str | Path):
    pages = ['1', '2']
    lista_pagina_demandas = []
    for page in pages:
        status_busca_demandas, dados_demandas = buscar_demandas(token, page)

        if status_busca_demandas == 200:
            lista_pagina_demandas.append(dados_demandas)
        else:
            raise Exception(f'Não foi possível acessar a API de busca de demandas do Assai: status {status_busca_demandas}')

    if len(lista_pagina_demandas) > 0:
        df_demandas = carregar_demandas(lista_pagina_demandas)
        salvar_demandas(df_demandas, path)


@st.cache_data
def ler_demandas(path: str | Path) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path, dtype={'id_agendamento': str, 'demanda': str}, parse_dates=['data_sugerida', 'data_efetiva'])
        df['data_efetiva'] = df['data_efetiva'].dt.strftime('%d/%m/%Y')
        df['data_sugerida'] = df['data_sugerida'].dt.strftime('%d/%m/%Y')
        df.sort_values(by='demanda')

        return df
    else:
        return pd.DataFrame()