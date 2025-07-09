import pandas as pd
import streamlit as st
import plotly.express as px

# Leitura do arquivo Excel
df = pd.read_excel('vendas.xlsx')

# Configuração da página
st.set_page_config(page_title='Dash', layout='wide')

# Mapeamento dos meses para abreviações
meses_abreviados = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}


# Adicionando a coluna de meses abreviados
df['Mês Abreviado'] = df['Mês'].map(meses_abreviados)


ordem_meses= ['Jan','Feb', 'Mar' , 'Apr', 'May', 'Aug', 'Sep','Oct' ,'Nov', 'Dec']


df['Mês Abreviado'] = pd.Categorical(df['Mês Abreviado'], categories= ordem_meses, ordered = True)

# Reorganização das colunas
df = df.drop(columns=['@dropdown'])
colunas = df.columns.tolist()
colunas.remove('Mês Abreviado')
indice_ano = colunas.index('Ano')
colunas.insert(indice_ano + 1, 'Mês Abreviado')
df = df[colunas]

# Sidebar - Filtros
Ano = df['Ano'].dropna().unique()
Ano_opcoes = sorted(Ano)
Ano_opcoes.insert(0, "Todos")  # Adiciona a opção "Todos" como primeira opção
Ano_selecionado = st.sidebar.selectbox('Ano', Ano_opcoes)

Mes = df['Mês Abreviado'].dropna().unique()
Mes_opcoes = sorted(Mes)
Mes_opcoes.insert(0, "Todos")
Mes_selecionado = st.sidebar.selectbox("Mês", Mes_opcoes)

# Aplicação dos filtros
df_filtrado = df.copy()

if Ano_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Ano'] == Ano_selecionado]

if Mes_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Mês Abreviado'] == Mes_selecionado]

# Agrupamentos e gráficos
faturamento_marca = df_filtrado.groupby('Marca', as_index=False)['Faturamento'].sum()
faturamento_tipo_marca = df_filtrado.groupby(['Tipo', 'Marca'], as_index=False)['Faturamento'].sum()
faturamento_tipo = df_filtrado.groupby('Tipo', as_index=False)['Faturamento'].sum()
faturamento_total = df_filtrado.groupby(['Ano' , 'Marca'])['Lucro'].sum().reset_index()
lucro_mensal = df_filtrado.groupby(['Mês Abreviado', 'Tipo'])['Lucro'].sum().reset_index()

faturamento_total['Ano'] = faturamento_total['Ano'].astype(str)

fig_faturamento = px.bar(faturamento_marca, x='Marca', y='Faturamento',
                         title='Faturamento por Marca',
                         labels={'Marca': 'Marca', 'Faturamento': 'Faturamento'},
                         color='Marca')

fig_faturamento_Tipo = px.bar(faturamento_tipo_marca, x='Tipo', y='Faturamento',
                              title='Faturamento por Tipo de Produto',
                              
                              color='Marca')

fig_faturamento_total = px.line(faturamento_total, x= 'Ano', y='Lucro',
                               color='Marca',
                               title='Lucro por Marca')



fig_lucro_mensal = px.pie(lucro_mensal, names='Tipo' , values='Lucro',
                          title= 'Lucro mensal por peça ',
                          hole=0.2,
                          color = 'Tipo')



fig_faturamento.update_layout(
    showlegend=False
)


fig_faturamento_total.update_layout(
    xaxis_title='Ano',
    yaxis_title='Lucro',
    xaxis=dict(
        tickmode='linear',
        dtick=1
    )
)






# Layout dos gráficos
col1, col2 = st.columns([1, 1])

with col1:
    st.plotly_chart(fig_faturamento)

with col2:
    st.plotly_chart(fig_faturamento_Tipo)

col3, col4 = st.columns([1, 1])

with col3:
    st.plotly_chart(fig_faturamento_total)

with col4:
    st.plotly_chart(fig_lucro_mensal)

# Exibindo o DataFrame filtrado
#st.write(df_filtrado)
