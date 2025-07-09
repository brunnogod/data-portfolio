import streamlit as st
import pandas as pd
import plotly.express as px

# Função para formatar valores grandes com unidades apropriadas
def format_value(value, unit="ton"):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} B {unit}"  # Bilhões
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} M {unit}"  # Milhões
    elif value >= 1_000:
        return f"{value / 1_000:.2f} K {unit}"  # Milhares
    else:
        return f"{value:.2f} {unit}"  # Menos que mil

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard MTR", layout="wide")

# CSS para customização do título e da sidebar
st.markdown("""
    <style>
    /* Ajusta a margem superior do título */
    .css-1e6f8y3 {
        margin-top: -50px; /* Ajuste esse valor conforme necessário */
    }
    /* Cor de fundo da sidebar */
    .css-1d391kg {
        background-color: #f5f5f5; /* Cinza claro */
    }
    /* Cor do texto da sidebar */
    .css-1d391kg .css-18e3n80 {
        color: #333; /* Texto escuro */
    }
    /* Cor dos elementos da sidebar */
    .css-1d391kg .css-1r4w6kq {
        background-color: #ffffff; /* Branco para os elementos */
        color: #000000; /* Texto escuro */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='margin-top: -50px;'>Dashboard MTR</h1>", unsafe_allow_html=True)

# Adicionando a logo na sidebar
st.sidebar.image('logo_sinir_negativa1.png', use_container_width=True)

# Lendo o arquivo Excel
df = pd.read_excel('RelatorioMTRs.xlsx')

df = df.fillna("Não Informado")

df[['codigo', 'residuos']] = df['Resíduo Cód/Descrição'].str.split('-', n=1, expand=True)
df.drop(columns=['Resíduo Cód/Descrição'], inplace=True)

df['Data de Recebimento'] = df['Data de Recebimento'].replace("Não Informado", pd.NaT)
df['Data de Recebimento'] = pd.to_datetime(df['Data de Recebimento'], errors='coerce')

df['Ano'] = df['Data de Recebimento'].dt.year
df['Mês'] = df['Data de Recebimento'].dt.strftime('%B')

Ano = df['Ano'].dropna().unique()
Ano_selecionado = st.sidebar.selectbox("Ano", sorted(Ano))

# Sidebar: filtro de mês com opção "Todos"
Mes = df['Mês'].dropna().unique()
Mes_opcoes = sorted(Mes)
Mes_opcoes.insert(0, "Todos")  # Adiciona a opção "Todos" como primeira opção
Mes_selecionado = st.sidebar.selectbox("Mês", Mes_opcoes)

# Filtros para a coluna "Tratamento" e "Resíduos"
tratamento_opcoes = ['Todos'] + df['Tratamento'].dropna().unique().tolist()
tratamento_selecionado = st.sidebar.selectbox("Tipo tratamento", tratamento_opcoes)

residuos_opcoes = ['Todos'] + df['residuos'].dropna().unique().tolist()
residuos_selecionado = st.sidebar.selectbox("Tipo resíduo", residuos_opcoes)

# Aplicar os filtros de ano, mês, tratamento e resíduos
df_filtrado = df[df['Ano'] == Ano_selecionado]

if Mes_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Mês'] == Mes_selecionado]

if tratamento_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Tratamento'] == tratamento_selecionado]

if residuos_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['residuos'].str.contains(residuos_selecionado, na=False, regex=False)]

# Calcular a quantidade total de Destinadores, Transportadores e Geradores únicos
total_destinadores = df_filtrado['Destinador (CNPJ/CPF)'].nunique()
total_transportadores = df_filtrado['Transportador (CNPJ/CPF)'].nunique()
total_geradores = df_filtrado['Gerador (CNPJ/CPF)'].nunique()

total = total_destinadores + total_transportadores + total_geradores

total_mtrs = df_filtrado['Numeros MTR'].nunique()

total_residuos = df_filtrado['Quantidade recebida'].sum()
total_residuos_formatado = format_value(total_residuos)

df_situacao = df_filtrado.groupby('Situação')['Numeros MTR'].nunique().reset_index()
df_tratamento = df_filtrado.groupby('Tratamento')['Quantidade recebida'].sum().reset_index()
df_classe_residuos = df_filtrado.groupby('Classe')['Quantidade recebida'].sum().reset_index()  # Adicionei essa linha para o gráfico de classe

df_certificado = df_filtrado['Certificado destinacao final'].nunique()

# Lista de cores para os gráficos de pizza
cores_pizza = ['#5a9591', '#314559', '#e8f595', '#fff', '#000', '#071d41', 'rgba(49,69,89,0.6)', '#4d8a86', '#afd4c7', '#bfdbd6']

# Gráfico de barras de quantidade de resíduos por mês
df_mensal = df_filtrado.groupby('Mês')['Quantidade recebida'].sum().reset_index()
df_mensal = df_mensal.sort_values('Mês', key=lambda x: pd.to_datetime(x, format='%B'))  # Ordenar pelos meses

# Gráfico de barras de CDF emitidos por mês
df_cdf_mensal = df_filtrado.groupby('Mês')['Certificado destinacao final'].nunique().reset_index()
df_cdf_mensal = df_cdf_mensal.sort_values('Mês', key=lambda x: pd.to_datetime(x, format='%B'))  # Ordenar pelos meses


# Gráfico de pizza de tratamento
fig_pizza_tratamento = px.pie(df_tratamento, names='Tratamento', values='Quantidade recebida',
                             title='Distribuição de Resíduos por Tratamento',
                             hole=0.2,
                             color_discrete_sequence=cores_pizza)
fig_pizza_tratamento.update_layout(
    title={
        'text': ' Resíduos por Tratamento',
        'x': 0.3,  # Centralizar o título
        'xanchor': 'center',
        'font': {
            'family': 'Segoe UI',
            'size': 20  # Tamanho da fonte do título
        }
    },
    margin=dict(t=80, b=60),
    legend=dict(
        title='Tratamento',
        orientation="v",
        yanchor="top",
        y=1.0,
        xanchor="left",
        x=1.1,
        title_font_size=16,
        font_size=12
    )
)

# Gráfico de pizza de classe resíduos 
fig_pizza_classe = px.pie(df_classe_residuos, names='Classe', values='Quantidade recebida',
                             title='Distribuição de Resíduos por Classe',
                             hole=0.2,
                             color_discrete_sequence=cores_pizza)
fig_pizza_classe.update_layout(
    title={
        'text': "Resíduos por Classe",
        'x': 0.4,
        'xanchor': 'center',
        'font': {
            'family': 'Segoe UI',
            'size': 20  # Tamanho da fonte do título
        }
    },
    margin=dict(t=80, b=60),
    legend=dict(
        title='Classe',
        orientation="v",
        yanchor="top",
        y=1.0,
        xanchor="left",
        x=1.1,
        title_font_size=16,
        font_size=12
    )
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <style>
    .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .metric-title {
        font-size: 24px; /* Tamanho da fonte do título */
        font-weight:;
        margin-bottom: 10px; /* Ajuste o espaçamento entre o título e o valor */
    }
    .metric-value {
        font-size: 28px; /* Tamanho da fonte do valor */
        font-weight: ;
    }
    </style>
    """, unsafe_allow_html=True)



# Exibir métricas
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    st.markdown('<div class="metric-container"><div class="metric-title">Total de Usuários</div><div class="metric-value">{}</div></div>'.format(total), unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-container"><div class="metric-title"> MTRs emitidos</div><div class="metric-value">{}</div></div>'.format(total_mtrs), unsafe_allow_html=True)
with col3:
   st.markdown('<div class="metric-container"><div class="metric-title">Total de resíduos</div><div class="metric-value">{}</div></div>'.format(total_residuos_formatado), unsafe_allow_html=True)
    
with col4:
    st.markdown('<div class="metric-container"><div class="metric-title">Total CDF emitidos</div><div class="metric-value">{}</div></div>'.format(df_certificado), unsafe_allow_html=True)

# Adicionando espaçamento
st.markdown("<br><br><br>", unsafe_allow_html=True)

# Exibindo gráficos de pizza
col7, col8 = st.columns([1, 1])
with col7:
    st.plotly_chart(fig_pizza_tratamento, use_container_width=True)
with col8:
    st.plotly_chart(fig_pizza_classe, use_container_width=True)



st.markdown("<br><br><br>", unsafe_allow_html=True)  # Adiciona espaçamento

# Adicionando a tabela de descrição dos resíduos com expander
fig_barras_mensal = px.bar(df_mensal, x='Mês', y='Quantidade recebida',
                          title='Quantidade de Resíduos Recebidos por Mês',
                          color_discrete_sequence=cores_pizza)

fig_barras_mensal.update_layout(
    title={
        'text': 'Total de resíduos recebidos por mês',
        'x': 0.5,  # Centralizar o título
        'xanchor': 'center',
        'font': {
            'family': 'Segoe UI',
            'size': 20  # Tamanho da fonte do título
        }
    },
     xaxis_title='Mês',
    yaxis_title='',
    yaxis=dict(
        showgrid=False, 
        showline=False, 
        zeroline=False, 
        title=None, 
        showticksuffix='none', 
        tickvals=[]  # Remove os valores dos ticks
    ),
    xaxis=dict(title='Mês'),
    margin=dict(t=80, b=60)
)

fig_barras_mensal.update_traces(
    text=df_mensal['Quantidade recebida'],  # Define os valores a serem exibidos
    texttemplate='%{text:.4f}',  # Formata o texto para não mostrar casas decimais
    textposition='outside'  # Posições dos textos
)

with st.expander("Quantidade de cada tipo de resíduos recebidos"):
    col1, col2 = st.columns([1, 1])  # Cria duas colunas com largura igual
    
    with col1:
        st.dataframe(df_filtrado[['residuos', 'Quantidade recebida']].drop_duplicates())
        
        with col2:
            st.plotly_chart(fig_barras_mensal)  # Exibe o gráfico na segunda coluna

# Criar o gráfico de barras
fig_barras_cdf = px.bar(df_cdf_mensal, x='Mês', y='Certificado destinacao final',
                        title='Certificados de Destinação Final por Mês',
                        color_continuous_scale=cores_pizza)

# Customizar a aparência do gráfico
fig_barras_cdf.update_layout(
    title={
        'text': 'Certificados de Destinação Final por Mês',
        'x': 0.5,  # Centralizar o título
        'xanchor': 'center',
        'font': {
            'family': 'Segoe UI',
            'size': 20  # Tamanho da fonte do título
        }
    },
    xaxis_title='Mês',
    yaxis_title='Número de CDFs',
    yaxis=dict(
        showgrid=False, 
        showline=False, 
        zeroline=False, 
        title=None, 
        showticksuffix='none', 
        tickvals=[]  # Remove os valores dos ticks
    ),
    xaxis=dict(title='Mês'),
    margin=dict(t=80, b=60)

)
fig_barras_cdf.update_traces(
    text=df_cdf_mensal['Certificado destinacao final'],  # Define os valores a serem exibidos
    texttemplate='%{text:.0f}',  # Formata o texto para não mostrar casas decimais
    textposition='outside'  # Posições dos textos
)



with st.expander("Total de CDF emitidos"):
  st.plotly_chart(fig_barras_cdf )  # Exibe o gráfico na segunda coluna
    
 
#formatar os valores dos gráficos em barras