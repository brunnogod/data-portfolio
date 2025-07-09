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

st.markdown("<h1 style='margin-top: -50px;'>Usuários cadastrados</h1>", unsafe_allow_html=True)

# Adicionando a logo na sidebar
st.sidebar.image('logo_sinir_negativa1.png', use_container_width=True)

# Lendo o arquivo Excel
df = pd.read_excel('RelatorioMTRs.xlsx')

df = df.fillna("Não Informado")

# --- IDENTIFICAR ESTADOS PELO NOME DO DESTINADOR E GERADOR ---

estados_keywords = {
    'AC': 'Acre', 'RIO BRANCO': 'Acre',
    'AL': 'Alagoas', 'MACEIÓ': 'Alagoas',
    'AM': 'Amazonas', 'MANAUS': 'Amazonas',
    'AP': 'Amapá', 'MACAPÁ': 'Amapá',
    'BA': 'Bahia', 'SALVADOR': 'Bahia',
    'CE': 'Ceará', 'FORTALEZA': 'Ceará',
    'DF': 'Distrito Federal', 'BRASÍLIA': 'Distrito Federal',
    'ES': 'Espírito Santo', 'VITÓRIA': 'Espírito Santo',
    'GO': 'Goiás', 'GOIÂNIA': 'Goiás',
    'MA': 'Maranhão', 'SÃO LUÍS': 'Maranhão',
    'MG': 'Minas Gerais', 'BELO HORIZONTE': 'Minas Gerais',
    'MS': 'Mato Grosso do Sul', 'CAMPO GRANDE': 'Mato Grosso do Sul',
    'MT': 'Mato Grosso', 'CUIABÁ': 'Mato Grosso',
    'PA': 'Pará', 'BELÉM': 'Pará',
    'PB': 'Paraíba', 'JOÃO PESSOA': 'Paraíba',
    'PE': 'Pernambuco', 'RECIFE': 'Pernambuco',
    'PI': 'Piauí', 'TERESINA': 'Piauí',
    'PR': 'Paraná', 'CURITIBA': 'Paraná',
    'RJ': 'Rio de Janeiro', 'RIO DE JANEIRO': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte', 'NATAL': 'Rio Grande do Norte',
    'RO': 'Rondônia', 'PORTO VELHO': 'Rondônia', 'CACOAL': 'Rondônia',
    'RR': 'Roraima', 'BOA VISTA': 'Roraima',
    'RS': 'Rio Grande do Sul', 'PORTO ALEGRE': 'Rio Grande do Sul',
    'SC': 'Santa Catarina', 'FLORIANÓPOLIS': 'Santa Catarina',
    'SE': 'Sergipe', 'ARACAJU': 'Sergipe',
    'SP': 'São Paulo', 'SÃO PAULO': 'São Paulo',
    'TO': 'Tocantins', 'PALMAS': 'Tocantins'
}

def identificar_estado_por_nome(nome_empresa):
    nome_upper = str(nome_empresa).upper()
    for keyword, estado in estados_keywords.items():
        if keyword in nome_upper:
            return estado
    return "Não Identificado"

df['Estado'] = df['Destinador (Nome)'].apply(identificar_estado_por_nome)
df['Estado_Gerador'] = df['Gerador (Nome)'].apply(identificar_estado_por_nome)

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

# ENCURTAR NOMES DOS DESTINADORES E GERADORES
df_filtrado['Destinador_Curto'] = df_filtrado['Destinador (Nome)'].apply(
    lambda x: x[:35] + "..." if len(str(x)) > 35 else str(x)
)

df_filtrado['Gerador_Curto'] = df_filtrado['Gerador (Nome)'].apply(
    lambda x: x[:35] + "..." if len(str(x)) > 35 else str(x)
)

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

df_certificado = df_filtrado['Certificado destinacao final'].nunique()

# Contar o número de geradores únicos por mês
df_geradores_por_mes = df_filtrado.groupby('Mês')['Gerador (CNPJ/CPF)'].nunique().reset_index()
df_geradores_por_mes = df_geradores_por_mes.sort_values(by='Mês', key=lambda x: pd.to_datetime(x, format='%B').dt.month)

# Contar o número de destinadores únicos por mês
df_destinadores_por_mes = df_filtrado.groupby('Mês')['Destinador (CNPJ/CPF)'].nunique().reset_index()
df_destinadores_por_mes = df_destinadores_por_mes.sort_values(by='Mês', key=lambda x: pd.to_datetime(x, format='%B').dt.month)

# Contar o número de transportadores únicos por mês
df_transportadores_por_mes = df_filtrado.groupby('Mês')['Transportador (CNPJ/CPF)'].nunique().reset_index()
df_transportadores_por_mes = df_transportadores_por_mes.sort_values(by='Mês', key=lambda x: pd.to_datetime(x, format='%B').dt.month)

# Lista de cores personalizadas para os gráficos de barras
cores_geradores= ['rgba(49,69,89,0.6)']
cores_destinadores = ['rgb(49, 99, 83)']
cores_transportadores = ['rgb(245, 251, 177)']

# Gráfico de barras para a quantidade de geradores por mês
fig_geradores_por_mes = px.bar(df_geradores_por_mes, 
                               x='Mês', 
                               y='Gerador (CNPJ/CPF)', 
                               title='Quantidade de Geradores por Mês',
                               labels={'Gerador (CNPJ/CPF)': 'Quantidade de Geradores', 'Mês': 'Mês'},
                               color_discrete_sequence=cores_geradores)
fig_geradores_por_mes.update_layout(
    title={
        'text': ' Geradores por mês',
        'x': 0.5,
        'xanchor': 'center',
        'font': {
            'family':'Segoe UI',
            'size': 20
        }
    },
   xaxis_title='Mês',
    yaxis_title='',
    yaxis= dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None, 
        showticksuffix='none', 
        tickvals=[]
    ),
    xaxis=dict(title='Mês'),
    margin=dict(t=80, b=60)
)

fig_geradores_por_mes.update_traces(
    text=df_geradores_por_mes['Gerador (CNPJ/CPF)'],
    texttemplate='%{text:.0f}',
    textposition='outside'
)

# Gráfico de barras para a quantidade de destinadores por mês
fig_destinadores_por_mes = px.bar(df_destinadores_por_mes, 
                                   x='Mês', 
                                   y='Destinador (CNPJ/CPF)', 
                                   title='Quantidade de Destinadores por Mês',
                                   color_discrete_sequence=cores_destinadores )
fig_destinadores_por_mes.update_layout(
    title={
        'text': ' Destinadores por mês',
        'x': 0.5,
        'xanchor': 'center',
        'font': {
            'family':'Segoe UI',
            'size': 20
        }
    },
    xaxis_title='Mês',
    yaxis_title='',
    yaxis= dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None, 
        showticksuffix='none', 
        tickvals=[]
    ),
    xaxis=dict(title='Mês'),
    margin=dict(t=80, b=60)
)

fig_destinadores_por_mes.update_traces(
    text=df_destinadores_por_mes['Destinador (CNPJ/CPF)'],
    texttemplate='%{text:.0f}',
    textposition='outside'
)

# Gráfico de barras para a quantidade de transportadores por mês
fig_transportadores_por_mes = px.bar(
    df_transportadores_por_mes, 
    x='Mês', 
    y='Transportador (CNPJ/CPF)', 
    title=' Transportadores por Mês',
    labels={'Transportador (CNPJ/CPF)': 'Quantidade de Transportadores', 'Mês': 'Mês'},
    color_discrete_sequence=cores_transportadores
)

fig_transportadores_por_mes.update_layout(
    title={
        'text': 'Transportadores por mês',
        'x': 0.5,
        'xanchor': 'center',
        'font': {
            'family':'Segoe UI',
            'size': 20
        }
    },
    xaxis_title='Mês',
    yaxis_title='',
    yaxis= dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        title=None, 
        showticksuffix='none', 
        tickvals=[]
    ),
    xaxis=dict(title='Mês'),
    margin=dict(t=80, b=60)
)

fig_transportadores_por_mes.update_traces(
    text=df_transportadores_por_mes['Transportador (CNPJ/CPF)'],
    texttemplate='%{text:.0f}',
    textposition='outside'
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
        font-size: 24px;
        font-weight:;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: ;
    }
    </style>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-container"><div class="metric-title">Total de Usuários</div><div class="metric-value">{}</div></div>'.format(total), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container"><div class="metric-title">Total de Destinadores</div><div class="metric-value">{}</div></div>'.format(total_destinadores), unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-container"><div class="metric-title">Total de Transportadores</div><div class="metric-value">{}</div></div>'.format(total_transportadores), unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-container"><div class="metric-title">Total de Geradores</div><div class="metric-value">{}</div></div>'.format(total_geradores), unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)

# Criando as colunas para os gráficos
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig_geradores_por_mes, use_container_width=True)

with col2:
    st.plotly_chart(fig_transportadores_por_mes, use_container_width=True)

with col3:
    st.plotly_chart(fig_destinadores_por_mes, use_container_width=True)

# ============= GRÁFICO DE PIZZA PARA DESTINADORES =============

# Preparar dados para o gráfico de pizza dos Destinadores
df_pizza_destinador = df_filtrado.groupby('Destinador (Nome)').agg({
    'Quantidade recebida': 'sum'
}).reset_index()

# Garantir que a coluna "Quantidade recebida" seja numérica
df_pizza_destinador['Quantidade recebida'] = pd.to_numeric(df_pizza_destinador['Quantidade recebida'], errors='coerce').fillna(0)

# Gráfico de pizza para Destinador - COM NOMES COMPLETOS NA LEGENDA
fig_pizza_destinador = px.pie(
    df_pizza_destinador, 
    names='Destinador (Nome)',  # Nome completo na legenda
    values='Quantidade recebida',
    title='Distribuição de Quantidade Recebida por Destinador'
)

fig_pizza_destinador.update_traces(
    textinfo='percent',
    textposition='inside',
    textfont_size=12,
    hovertemplate='<b>%{label}</b><br>' +
                  'Quantidade: %{value:,.0f}<br>' +
                  'Percentual: %{percent}<br>' +
                  '<extra></extra>'
)

fig_pizza_destinador.update_layout(
    height=500,  # Altura reduzida
    width=600,   # Largura reduzida
    title={
        'text': 'Distribuição por Destinador',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18}  # Fonte menor
    },
    margin=dict(t=60, b=40, l=40, r=40),  # Margens reduzidas
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=9)  # Fonte da legenda menor
    )
)

# ============= GRÁFICO DE PIZZA PARA GERADORES =============

# Preparar dados para o gráfico de pizza dos Geradores
df_pizza_gerador = df_filtrado.groupby('Gerador (Nome)').agg({
    'Quantidade recebida': 'sum'
}).reset_index()

# Garantir que a coluna "Quantidade recebida" seja numérica
df_pizza_gerador['Quantidade recebida'] = pd.to_numeric(df_pizza_gerador['Quantidade recebida'], errors='coerce').fillna(0)

# Gráfico de pizza para Gerador - COM NOMES COMPLETOS NA LEGENDA
fig_pizza_gerador_new = px.pie(
    df_pizza_gerador, 
    names='Gerador (Nome)',  # Nome completo na legenda
    values='Quantidade recebida',
    title='Distribuição de Quantidade Recebida por Gerador'
)

fig_pizza_gerador_new.update_traces(
    textinfo='percent',
    textposition='inside',
    textfont_size=12,
    hovertemplate='<b>%{label}</b><br>' +
                  'Quantidade: %{value:,.0f}<br>' +
                  'Percentual: %{percent}<br>' +
                  '<extra></extra>'
)

fig_pizza_gerador_new.update_layout(
    height=500,  # Altura reduzida
    width=600,   # Largura reduzida
    title={
        'text': 'Distribuição por Gerador',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 18}  # Fonte menor
    },
    margin=dict(t=60, b=40, l=40, r=40),  # Margens reduzidas
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        font=dict(size=9)  # Fonte da legenda menor
    )
)

# Expander com gráfico de pizza para Destinadores - TABELA À ESQUERDA
with st.expander("Distribuição de Quantidade por Destinador"):
    col1, col2 = st.columns([1, 2])  # Tabela menor, Pizza maior
    
    with col1:
        # Tabela com informações dos destinadores
        df_info_destinador = df_filtrado.groupby('Destinador (Nome)').agg({
            'Quantidade recebida': 'sum',
            'Observação Destinador': 'first'
        }).reset_index()
        st.subheader("Informações dos Destinadores")
        st.dataframe(df_info_destinador, height=450)
    
    with col2:
        st.plotly_chart(fig_pizza_destinador, use_container_width=True, height=500)

# Expander para Gerador com pizza - TABELA À ESQUERDA
with st.expander("Observação Gerador / Distribuição por Gerador"):
    col1, col2 = st.columns([1, 2])  # Tabela menor, Pizza maior

    with col1:
        # Tabela com informações dos geradores
        df_info_gerador = df_filtrado.groupby('Gerador (Nome)').agg({
            'Quantidade recebida': 'sum',
            'Observação Gerador': 'first'
        }).reset_index()
        st.subheader("Informações dos Geradores")
        st.dataframe(df_info_gerador, height=450)

    with col2:
        st.plotly_chart(fig_pizza_gerador_new, use_container_width=True, height=500)