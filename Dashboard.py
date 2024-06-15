import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Colocando esta configuração por padrão no navegador
# Turn on to make this app occupy the entire width of the screen
st.set_page_config(layout='wide')


def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil', 'milhões']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} {unidade}'  # Caso valor seja muito grande


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Pegando endereço da API
url = 'https://labdados.com/produtos'

# para filtros barra lateral sidebar
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}


########################################################################################

response = requests.get(url, params=query_string)

# transformando para json e depois o json é transformado em um dataframe
dados = pd.DataFrame.from_dict(response.json())

# alterando o tipo do campus
dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect(
    'Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(
    receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(
    pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[
    ['Preço']].sum().sort_values('Preço', ascending=False)

# Tabelas de quantidades de vendas


# Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')[
                          'Preço'].agg(['sum', 'count']))


# Grácifos

# gráfico de mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita por estado',
                                  )

# grafico de linha
fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             color='Ano',
                             template='seaborn',
                             title='Receita mensal',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             line_dash='Ano'
                             )

fig_receita_mensal.update_layout(yaxis_title='Receita mensal')

# Gráfico de barra
fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title='Receita')


# Visualização no streamlit
aba1, aba2, aba3, aba4 = st.tabs(
    ['Receita', 'Quantidade de vendas', 'Vendedores', 'Tabela'])


# col1, col2 = st.columns(2)  # variaveis que vão amazenar as colunas

# métodos de fazer

# método 01
# col1.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
# col2.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
# col3.metric(label="Temperature", value="70 °F", delta="1.2 °F")

# método 02
# with col1:   # utilizaremos a cláusula with. Essa cláusula nos permite acessar cada coluna e inserir elementos.
#     st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
# with col2:
#     st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
# with col3:
#     st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
# Visualização no streamlit


with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))


with aba3:
    qtd_vendedores = st.number_input('Quantidade de vedendores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))

        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values(
                                            'sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                            x='count',
                            y=vendedores[['count']].sort_values(
            'count', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_receita_vendedores)

with aba4:
    coluna1, coluna2 = st.columns(2)

    st.dataframe(dados)


# st.dataframe(dados)
