import dash
from dash import dcc, html
import pandas as pd
from sqlalchemy import create_engine
import os
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do banco de dados
db_config = {
    'dbname': os.getenv("POSTGRES_DB", "gpus_db"),
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'password': os.getenv("POSTGRES_PASSWORD", "postgres"),
    'host': os.getenv("POSTGRES_HOST", "192.168.18.235"),
    'port': os.getenv("POSTGRES_PORT", "5432")
}

# Função para conectar ao banco e buscar os dados
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
        logger.info(f"Dados carregados: {len(df)} linhas")
        if df.empty:
            logger.warning("DataFrame vazio. Verifique se as tabelas têm dados.")
        else:
            logger.info(f"Primeiras linhas do DataFrame:\n{df.head()}")
        return df
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return pd.DataFrame()

# Carregar os dados
df = fetch_data()

# Inicializar o app Dash
app = dash.Dash(__name__, external_scripts=[
    "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"  # Carregar ECharts via CDN
])

# Criar opções para o dropdown
gpu_options = [{'label': 'Todas as Placas', 'value': 'Todas as Placas'}] + \
              [{'label': f"{row['marca']} {row['nome']}", 'value': f"{row['marca']} {row['nome']}"}
               for _, row in df.drop_duplicates(['marca', 'nome']).iterrows()]

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Preços de Placas de Vídeo"),
    
    # Dropdown para selecionar a GPU
    dcc.Dropdown(
        id='gpu-dropdown',
        options=gpu_options,
        value='Todas as Placas',
        placeholder="Selecione uma GPU",
        style={'width': '50%'}
    ),
    
    # Div para o gráfico ECharts
    html.Div(id='price-graph', style={'width': '100%', 'height': '400px'})
])

# Callback para atualizar o gráfico
@app.callback(
    dash.dependencies.Output('price-graph', 'children'),
    [dash.dependencies.Input('gpu-dropdown', 'value')]
)
def update_graph(selected_gpu):
    logger.info(f"Atualizando gráfico para GPU: {selected_gpu}")
    
    if not selected_gpu or df.empty:
        logger.warning("Nenhum dado disponível ou GPU não selecionada.")
        return html.Div("Nenhum dado disponível")

    # Filtrar os dados
    try:
        if selected_gpu == 'Todas as Placas':
            filtered_df = df.copy()
            filtered_df['gpu'] = filtered_df['marca'] + ' ' + filtered_df['nome']
        else:
            marca, nome = selected_gpu.split(' ', 1)
            filtered_df = df[(df['marca'] == marca) & (df['nome'] == nome)]
            filtered_df['gpu'] = filtered_df['marca'] + ' ' + filtered_df['nome']

        if filtered_df.empty:
            logger.warning(f"Nenhum dado encontrado para a GPU: {selected_gpu}")
            return html.Div(f"Nenhum dado encontrado para {selected_gpu}")

        logger.info(f"Dados filtrados: {len(filtered_df)} linhas")

        # Preparar os dados para ECharts
        data_by_website = {}
        for website in filtered_df['website'].unique():
            website_df = filtered_df[filtered_df['website'] == website]
            website_df = website_df.sort_values('data')  # Ordenar por data
            data_by_website[website] = [
                [row['data'].strftime('%Y-%m-%d'), float(row['preco'])]  # Garantir que preco é float
                for _, row in website_df.iterrows()
            ]

        logger.info(f"Dados preparados para ECharts: {data_by_website}")

        # Configuração do gráfico ECharts para replicar o estilo do Chart.js
        echarts_option = {
            'tooltip': {
                'trigger': 'axis',
                'formatter': "{b0}<br/>{a0}: {c0} R$"
            },
            'legend': {
                'top': '0%',  # Posicionar a legenda no topo
                'left': 'center'
            },
            'xAxis': {
                'type': 'time',
                'axisLabel': {
                    'formatter': '{dd} de {MMM}'  # Formato: "25 de Abr"
                }
            },
            'yAxis': {
                'type': 'value',
                'name': 'R$',
                'axisLabel': {
                    'formatter': 'R$ {value}'
                }
            },
            'series': [
                {
                    'name': website,
                    'type': 'line',
                    'data': data,
                    # Removido 'areaStyle' para não ter área sombreada
                    'showSymbol': False  # Não mostrar pontos nas linhas
                }
                for website, data in data_by_website.items()
            ]
        }

        # Converter echarts_option para string JSON
        echarts_option_json = json.dumps(echarts_option)

        # JavaScript para renderizar o gráfico ECharts
        echarts_script = f"""
        setTimeout(function() {{
            var chartDom = document.getElementById('echarts-graph');
            if (chartDom) {{
                var chart = echarts.init(chartDom);
                chart.setOption({echarts_option_json});
            }} else {{
                console.error('Elemento echarts-graph não encontrado');
            }}
        }}, 100);
        """

        logger.info("Gráfico ECharts configurado e script gerado.")

        return html.Div([
            html.Div(id='echarts-graph', style={'width': '100%', 'height': '400px'}),
            html.Script(echarts_script)
        ])
    except Exception as e:
        logger.error(f"Erro ao atualizar o gráfico: {e}")
        return html.Div(f"Erro ao gerar o gráfico: {str(e)}")

# Rodar o servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
