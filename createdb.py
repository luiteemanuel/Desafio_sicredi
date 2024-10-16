import sqlite3
import pandas as pd

df_faixa_risco = pd.read_csv('db_credito.faixas_risco_1_(1).csv',sep=';',encoding='latin1')
df_credito_operacoes = pd.read_csv('db_credito.operacoes_1_(1).csv',sep=';',encoding='latin1')


def create_db():
    conn = sqlite3.connect('sicredi_teste.db')
    cursor = conn.cursor()

    df_faixa_risco.to_sql('faixa_risco', conn, if_exists='replace', index=False)
    df_credito_operacoes.to_sql('credito_operacoes', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

create_db()

