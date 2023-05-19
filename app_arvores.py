import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

# Configurações básicas da página
st.set_page_config(
    page_title='Dashboard Árvores',
    page_icon=':seedling:',
    layout='wide'
)

# Busca os dados na planilha
df = pd.read_excel(
    io='especies_recomendadas_final_1.xlsx',
    engine='openpyxl'
)

# Sidebar com seleção de filtros (Origem, Porte e Deciduidade)
st.sidebar.header('Filtrar por:')
origem = st.sidebar.multiselect(
    'Origem:',
    options=df['Origem'].unique(),
    default=df['Origem'].unique()
)

porte = st.sidebar.multiselect(
    'Porte:',
    options=df['Porte'].unique(),
    default=df['Porte'].unique()
)

deciduidade = st.sidebar.multiselect(
    'Deciduidade:',
    options=df['Deciduidade'].unique(),
    default=df['Deciduidade'].unique()
)

# Atualiza o dataframe com os filtros selecionados
df_selection = df.query(
    'Origem==@origem & Porte==@porte & Deciduidade==@deciduidade'
)

# Título principal da página
st.title(':seedling: Dashboard Árvores')
st.markdown('##')

# Total de tipos de árvore, altura média e diâmetro médio das árvores
total_tipos_de_arvore = len(df_selection['Nome_popular'])
altura_media = round(df_selection['Altura_(m)'].mean(), 1)
diametro_medio = round(df_selection['Diâmetro_(cm)'].mean(), 1)

# Exibe total_tipos_de_arvore, altura_media e diametro_medio
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Tipos de árvore:')
    st.subheader(f'{total_tipos_de_arvore}')
with middle_column:
    st.subheader('Altura média:')
    st.subheader(f'{altura_media} m')
with right_column:
    st.subheader('Diâmetro médio:')
    st.subheader(f'{diametro_medio} cm')

st.markdown('---')

# Exibe o dataframe filtrado
st.dataframe(df_selection)

# Calcula o diâmetro médio das árvores para cada origem e gera um gráfico de barras
if not df_selection.empty:
    diametro_medio_por_origem = (
        df_selection.groupby(by=['Origem']).mean()[['Diâmetro_(cm)']].sort_values(by='Origem')
    )

    grafico_diametro_medio_por_origem = px.bar(
        diametro_medio_por_origem,
        x=diametro_medio_por_origem.index,
        y='Diâmetro_(cm)',
        orientation='v',
        title='<b>Diâmetro médio por origem</b>',
        color_discrete_sequence = ['#0083B8']*len(diametro_medio_por_origem),
        template='plotly_white'
    )

    grafico_diametro_medio_por_origem.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=({'showgrid': False})
    )

# Gera gráfico de pizza do porte das árvores
    p_qtd = len(df_selection.loc[df_selection['Porte']=='P'])
    m_qtd = len(df_selection.loc[df_selection['Porte']=='M'])
    g_qtd = len(df_selection.loc[df_selection['Porte']=='G'])

    porte_porcentagem = [round((p_qtd/total_tipos_de_arvore)*100, 1),
                        round((m_qtd/total_tipos_de_arvore)*100, 1),
                        round((g_qtd/total_tipos_de_arvore)*100, 1)]

    porte_rotulos = [   'P ('+str(porte_porcentagem[0])+'%)',
                        'M ('+str(porte_porcentagem[1])+'%)',
                        'G ('+str(porte_porcentagem[2])+'%)']
 
    grafico_porte_arvores = px.pie(
        values=porte_porcentagem,
        names=porte_rotulos,
        title='<b>Percentual dos portes</b>'
    )

# Exibe gráficos lado a lado
    left_column, right_column = st.columns(2)
    left_column.plotly_chart(grafico_diametro_medio_por_origem, use_container_width=True)
    right_column.plotly_chart(grafico_porte_arvores, use_container_width=True)

# Ideia inicial de ML - Previsão de terreno necessário para plantio
st.subheader('Previsão de terreno')
st.markdown('Insira a altura de árvore desejada para prever o diâmetro que esta ocupará.')
st.markdown('Isto facilitará a preparação prévia do terreno para o plantio.')

input = st.text_input('Altura (em metros)')

df = pd.read_excel('especies_recomendadas_final_train.xlsx')
x = df['Altura_(m)']
y = df['Diâmetro_(cm)']
slope, intercept, r, p, std_err = stats.linregress(x, y)

def previsao(x):
  return float(slope) * float(x) + intercept

if (not(input == '')):
    diametro = previsao(input)
    st.markdown('Esta árvore ocupará cerca de **'+str(round(diametro, 1))+' cm** em diâmetro.')
