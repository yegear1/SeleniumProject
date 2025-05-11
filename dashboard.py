from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine

from dash import dcc, html
import dash

import plotly.express as px
import pandas as pd

import psycopg2
import logging
import os

logger = logging.getLogger("main")

db_config = {
    'dbname': os.getenv("POSTGRES_DB", "gpus_db"),
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'password': os.getenv("POSTGRES_PASSWORD", "postgres"),
    'host': os.getenv("POSTGRES_HOST", "192.168.18.235"),
    'port': os.getenv("POSTGRES_PORT", "5600")
}

def fetch_data():
    try:
        conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        engine = create_engine(conn_str)

        query = """ 
        SELECT g.marca, g.nome, w.name AS website, p.preco, p.data
        FROM gpu_prices p
        JOIN gpu_info g ON p.gpu_id = g.id
        JOIN website_id w ON p.website_id = w.id 
        """
        df = pd.read_sql(query, engine)
        engine.dispose()
        print(f"Dados carregados: {len(df)} linhas")
        if df.empty:
            print("DataFrame vazio. Verifique se as tabelas têm dados.")
        else:
            print(df.head())

        return df
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return pd.DataFrame()

    
df = fetch_data()

app = dash.Dash(__name__)

gpu_options = [{'label': 'Todas as Placas', 'value': 'Todas as Placas'}] + \
              [{'label': f"{row['marca']} {row['nome']}", 'value': f"{row['marca']} {row['nome']}"}
               for _, row in df.drop_duplicates(['marca', 'nome']).iterrows()]

app.layout = html.Div([
    html.H1("Dashboard de Preços de Placas de Vídeo"),
    
    # Dropdown para selecionar a GPU
    dcc.Dropdown(
        id='gpu-dropdown',
        options=gpu_options,
        value='Todas as Placas',  # Valor inicial
        placeholder="Selecione uma GPU",
        style={'width': '50%'}
    ),
    
    # Gráfico de preços ao longo do tempo
    dcc.Graph(id='price-graph')
])

@app.callback(
    dash.dependencies.Output('price-graph', 'figure'),
    [dash.dependencies.Input('gpu-dropdown', 'value')]
)

def update_graph(selected_gpu):
    if not selected_gpu or df.empty:
        return px.line(title="Nenhum dado disponível")
    
    if selected_gpu == 'Todas as Placas':
        # Mostrar todas as GPUs, separadas por site
        filtered_df = df.copy()
        # Criar uma coluna para identificar a GPU no gráfico
        filtered_df['gpu'] = filtered_df['marca'] + ' ' + filtered_df['nome']
        fig = px.line(
            filtered_df,
            x='data',
            y='preco',
            color='website',
            line_group='gpu',  # Diferenciar linhas por GPU
            hover_data=['gpu'],  # Mostrar o nome da GPU ao passar o mouse
            title='Preço de Todas as Placas ao Longo do Tempo',
            labels={'data': 'Data', 'preco': 'Preço (R$)', 'website': 'Site'}
        )
    else:
        # Filtrar os dados para a GPU selecionada
        marca, nome = selected_gpu.split(' ', 1)
        filtered_df = df[(df['marca'] == marca) & (df['nome'] == nome)]
        fig = px.line(
            filtered_df,
            x='data',
            y='preco',
            color='website',
            title=f'Preço de {selected_gpu} ao longo do tempo',
            labels={'data': 'Data', 'preco': 'Preço (R$)', 'website': 'Site'}
        )
    
    return fig

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
