import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    df_db_operacoes = pd.read_csv('db_credito.operacoes_1_(1).csv', sep=';')
    df_db_faixa_risco = pd.read_csv('db_credito.faixas_risco_1_(1).csv', sep=';', encoding='latin1')
    df_dados_case = pd.read_excel('dados_case_analista_dados_1_(1).xlsx', sheet_name='DADOS')
    aposentados = df_dados_case[df_dados_case['DESC_CBO'] == 'Aposentados e beneficiários do inss']
    return df_db_operacoes, df_db_faixa_risco, df_dados_case, aposentados

df_db_operacoes, df_db_faixa_risco, df_dados_case, aposentados = load_data()

@st.cache_data
def get_distribuicao_renda(aposentados):
    distribuicao_renda = aposentados['RENDA_CAT'].value_counts(normalize=True).reset_index()
    distribuicao_renda.columns = ['RENDA_CAT', 'Proporção']
    distribuicao_renda['Proporção_formatada'] = distribuicao_renda['Proporção'].apply(lambda x: f"{x:.2%}")
    return distribuicao_renda

distribuicao_renda = get_distribuicao_renda(aposentados)

def limpar_e_converter(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    return pd.to_numeric(serie.replace({'S': 1, 'N': 0, 'SN': np.nan}), errors='coerce')

@st.cache_data
def analise_completa_sicredi(renda_cat, aposentados):
    aposentados_filtrados = aposentados[aposentados['RENDA_CAT'] == renda_cat]
    
    produtos_servicos = [
        'PROD_CESTA_RELACIONAMENTO', 'PROD_DEBITO_CONTA', 'PROD_POUPANCA', 
        'PROD_FUNDOS', 'PROD_PREVIDENCIA', 'PROD_SEGURO_RESIDENCIAL', 
        'PROD_SEGURO_AUTOMOVEL', 'DIGITAL_TRANSACIONOU_30D', 'DIGITAL_ACESSOU_30D', 'POSSUI_CAD_DIGITAL'
    ]
    
    utilizacao = aposentados_filtrados[produtos_servicos].apply(limpar_e_converter).mean().sort_values(ascending=False)
    
    return utilizacao

st.title('Análise Sicredi - Case Luiza')
st.markdown("## *1º Tópico*")

categorias_renda = aposentados['RENDA_CAT'].unique()
renda_selecionada = st.selectbox('Selecione a categoria de renda:', categorias_renda)

resultados = analise_completa_sicredi(renda_selecionada, aposentados)

st.write(f"Análise para categoria de renda: {renda_selecionada}")
st.subheader('Taxa de Utilização de Produtos e Serviços')
df_display = resultados.reset_index().rename(columns={'index': 'Produto/Serviço', 0: 'Taxa de Utilização'})
df_display['Taxa de Utilização'] = df_display['Taxa de Utilização'].apply(lambda x: f'{x:.2%}')
st.dataframe(df_display, use_container_width=True)

fig, ax = plt.subplots(figsize=(12, 8))
colors = sns.color_palette("viridis", n_colors=len(resultados))
bars = sns.barplot(x=resultados.index, y=resultados.values, ax=ax, palette=colors)

for i, v in enumerate(resultados.values):
    ax.text(i, v, f'{v:.1%}', ha='center', va='bottom')

plt.title('Taxa de Utilização de Produtos e Serviços', fontsize=16, fontweight='bold')
plt.xlabel('Produtos e Serviços', fontsize=12)
plt.ylabel('Taxa de Utilização', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

st.pyplot(fig)

st.info("""
**Explicação dos Dados:**
- **Taxa de Utilização**: Representa a proporção de clientes que utilizam cada produto ou serviço.
- **Produtos/Serviços**: Inclui diversos produtos financeiros e serviços digitais oferecidos pelo Sicredi.
- Os dados são específicos para a categoria de renda selecionada e focam em clientes aposentados.
""")

st.subheader('Top 5 Regiões com Maior Número de Associados')

crescimento_regional = aposentados.groupby('DES_CENTRAL').agg({
    'CODIGO_ASSOC': 'count',
    'SALDO_CRÉDITO_PESSOAL': 'mean'
}).sort_values('CODIGO_ASSOC', ascending=False).head()

# Formatando o DataFrame para exibição
crescimento_regional_display = crescimento_regional.copy()
crescimento_regional_display['CODIGO_ASSOC'] = crescimento_regional_display['CODIGO_ASSOC'].astype(int)
crescimento_regional_display['SALDO_CRÉDITO_PESSOAL'] = crescimento_regional_display['SALDO_CRÉDITO_PESSOAL'].apply(lambda x: f'R$ {x:.2f}')

# Renomeando as colunas para melhor compreensão
crescimento_regional_display.columns = ['Número de Associados', 'Saldo Médio de Crédito Pessoal']

# Exibindo o DataFrame no Streamlit
st.dataframe(crescimento_regional_display)

# Adicionando uma explicação
st.info("""
**Explicação das Métricas Regionais:**
- **Número de Associados**: Total de clientes aposentados em cada região.
- **Saldo Médio de Crédito Pessoal**: Valor médio do saldo de crédito pessoal dos associados na região.
""")

st.subheader('Educação Financeira')

# Função para calcular a média de forma segura
def safe_mean(series):
    if pd.api.types.is_numeric_dtype(series):
        return series.mean()
    elif pd.api.types.is_object_dtype(series):
        # Tenta converter para numérico, tratando erros como NaN
        numeric_series = pd.to_numeric(series, errors='coerce')
        return numeric_series.mean()
    else:
        return np.nan

# Calculando as métricas de educação financeira
colunas_educacao = ['PROD_POUPANCA', 'PROD_FUNDOS', 'PROD_PREVIDENCIA', 
                    'DIGITAL_TRANSACIONOU_30D', 'DIGITAL_ACESSOU_30D', 'POSSUI_CAD_DIGITAL']

dados_educacao_financeira = aposentados.groupby('RENDA_CAT').agg({
    col: safe_mean for col in colunas_educacao
}).reset_index()

# Formatando o DataFrame para exibição
dados_educacao_financeira_display = dados_educacao_financeira.copy()
for col in colunas_educacao:
    dados_educacao_financeira_display[col] = dados_educacao_financeira_display[col].apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A')

# Renomeando as colunas para melhor compreensão
dados_educacao_financeira_display.columns = [
    'Categoria de Renda',
    'Uso de Poupança',
    'Uso de Fundos',
    'Uso de Previdência',
    'Transações Digitais (30d)',
    'Acessos Digitais (30d)',
    'Cadastro Digital'
]

# Exibindo o DataFrame no Streamlit
st.dataframe(dados_educacao_financeira_display)

# Adicionando uma explicação
st.info("""
**Explicação dos Indicadores de Educação Financeira:**
- **Uso de Poupança/Fundos/Previdência**: Percentual de clientes que utilizam esses produtos financeiros.
- **Transações/Acessos Digitais**: Percentual de clientes que realizaram transações ou acessaram canais digitais nos últimos 30 dias.
- **Cadastro Digital**: Percentual de clientes que possuem cadastro em canais digitais.

Estes indicadores ajudam a entender o nível de engajamento financeiro e digital dos clientes em diferentes categorias de renda.
""")


st.subheader('Com base nos dados analisados, pode oferecer produtos e suporte personalizado para Luiza e sua família. Podemos abordar isso em três aspectos principais:')

st.write('''
- **Educação Financeira**: Luiza e seus familiares podem receber orientações sobre como gerenciar melhor seus rendimentos e despesas.
- **Seguros**: A família pode ser incentivada a considerar a importância de proteção contra riscos como desemprego, doenças graves e outros imprevistos.
- **Investimentos**: Com a renda mais estável, a família pode explorar oportunidades de investimento, como poupança, fundos de investimento e previdência.
- **Credito consignado**: Avaliar a possibilidade de oferecer produtos de crédito consignado"
- 
''')

st.markdown("## *2º Tópico*")

st.subheader("Análise de Principalidade")

# Calculando a média de produtos utilizados por categoria de renda
produtos = ['PROD_POUPANCA', 'PROD_FUNDOS', 'PROD_PREVIDENCIA', 'PROD_SEGURO_RESIDENCIAL', 'PROD_SEGURO_AUTOMOVEL']
principalidade = aposentados.groupby('RENDA_CAT')[produtos].mean().sum(axis=1).reset_index()
principalidade.columns = ['Categoria de Renda', 'Média de Produtos Utilizados']

st.dataframe(principalidade)


st.write("Esta análise mostra como clientes em diferentes faixas de renda tendem a utilizar múltiplos produtos, indicando o potencial de principalidade.")

st.subheader("Análise de Utilização de Crédito")

credito_cols = ['SALDO_CARTOES', 'SALDO_CHEQUE_ESPECIAL', 'SALDO_CRÉDITO_PESSOAL', 'SALDO_IMOBILIARIO']
utilizacao_credito = aposentados.groupby('RENDA_CAT')[credito_cols].mean().reset_index()

st.dataframe(utilizacao_credito)

st.write("Esta análise mostra o uso médio de diferentes tipos de crédito por faixa de renda, indicando oportunidades para oferta de crédito sustentável.")

st.write("A Média de Produtos Utilizados é uma medida que indica quantos dos produtos listados um cliente típico de cada categoria de renda utiliza.")

st.subheader("Análise Regional")

regional_analysis = aposentados.groupby('DES_CENTRAL').agg({
    'CODIGO_ASSOC': 'count',
    'SCORE_PRINCIPALIDADE': 'mean',
    'SALDO_CRÉDITO_PESSOAL': 'mean'
}).reset_index()

regional_analysis.columns = ['Região', 'Número de Associados', 'Score Médio de Principalidade', 'Saldo Médio de Crédito Pessoal']

st.dataframe(regional_analysis)


st.write("Esta análise mostra como diferentes regiões se comparam em termos de número de associados, principalidade e uso de crédito.")


st.subheader("Como o Sicredi pode se beneficiar em ter Luiza como sócia")

st.write("""
Com base nas análises realizadas, podemos concluir que o Sicredi pode se beneficiar significativamente ao ter Luiza como sócia:

1. Engajamento e Principalidade:
   - A análise de utilização de produtos mostra que dependendo da faixa de renda de Luiza têm potencial para usar múltiplos produtos e serviços.
   - Isso aumenta a principalidade, fortalecendo o relacionamento entre Luiza e o Sicredi.

2. Oportunidades de Crédito:
   - Os dados de utilização de crédito por faixa de renda indicam oportunidades para oferecer produtos de crédito personalizados e sustentáveis.
   - Isso pode incluir opções como crédito pessoal, financiamentos ou microcrédito adaptados às necessidades de Luiza.
   - Vale ressaltar que necessário uma análise mais aprofundada do seu perfil para entender melhor suas necessidades.

3. Representatividade Regional:
   - A análise regional mostra como novos sócios como Luiza podem contribuir para fortalecer a presença do Sicredi em diferentes áreas.
   - Isso pode resultar em um crescimento orgânico da base de clientes na região de Luiza.

Ao focar nestes aspectos, o Sicredi não apenas se beneficia financeiramente, mas ainda mais o seu modelo cooperativo, melhorando e intendendo sobre as necessidades locais e contribuindo para o desenvolvimento sustentável da comunidade de Luiza.
""")