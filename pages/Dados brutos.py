import streamlit as st
import requests
import pandas as pd
import time

# criando cache para ficar mais otimizado



@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

st.title('DADOS BRUTOS')


# Pegando endereço da API
url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(
    dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(
        dados.columns), list(dados.columns))

st.sidebar.title('Filtros')


# Produto
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect(
        'Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

# Categoria do produto

with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione a Categoria', dados['Categoria do Produto'].unique(
    ), dados['Categoria do Produto'].unique())
    # categoria = st.selectbox('Selecione a Categoria',dados['Categoria do Produto'].unique())

# Preço do produto
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))

# Frete do produto
with st.sidebar.expander('Frete do produto'):
    frete = st.slider('Selecione o frete', 0, int(
        dados['Frete'].max()), (0, int(dados['Frete'].max())))


# Data da compra
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input(
        'Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

# Vendador
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect(
        'Selecione o vendedor(s)', dados['Vendedor'].unique(), dados['Vendedor'].unique())

# Local da compra
with st.sidebar.expander('Local da compra'):
    local = st.multiselect('Local da Compra', dados['Local da compra'].unique(
    ), dados['Local da compra'].unique())

# Avaliação da compra
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Avaliação da compra', 0, dados['Avaliação da compra'].max(
    ), (0, dados['Avaliação da compra'].max()))

# Tipo de pagamento
with st.sidebar.expander('Tipo de pagamentos'):
    pagamento = st.multiselect('Tipo de pagamento', dados['Tipo de pagamento'].unique(
    ), dados['Tipo de pagamento'].unique())

# Quantidade de parcelas
with st.sidebar.expander('Quantidade de parcelas'):
    qt_parcelas = st.slider('Quantidade de parcelas', 0, dados['Quantidade de parcelas'].max(
    ), (0, dados['Quantidade de parcelas'].max()))


dados_filtrados = dados.query(
    f''' `Produto` in {produtos} and\
    `Vendedor` in {vendedores} and\
    `Local da compra` in {local} and\
    `Tipo de pagamento` in {pagamento} and\
    `Categoria do Produto` in {categoria} and\
    '{data_compra[0]}' <= `Data da Compra` <= '{data_compra[1]}' and\
    {preco[0]} <= `Preço` <= {preco[1]} and\
    {frete[0]} <= `Frete` <= {frete[1]} and\
    {avaliacao[0]} <= `Avaliação da compra` <= {avaliacao[1]} and\
    {qt_parcelas[0]} <= `Quantidade de parcelas` <= {qt_parcelas[1]}''')

dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{
            dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')

# para exebir a mensagem de sucesso


def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()


coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados em csv')
    nome_arquivo += '.csv'

with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
    

         


# query = '''
# Produto in @produtos and \
# @preco[0] <= Preço <= @preco[1] and \
# @data_compra[0] <= `Data da Compra` <= @data_compra[1]
# '''

# dados_filtrados = dados.query(query)
# dados_filtrados = dados_filtrados[colunas]

# st.dataframe(dados_filtrados)
