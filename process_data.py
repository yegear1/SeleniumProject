import pandas as pd
import plotly.express as px

def process_data(csv_file="gpu_data.csv"):
    """
    Processa o CSV gerado pelo scraping, faz tratamentos e cria um dashboard.
    
    Args:
        csv_file (str): Caminho do arquivo CSV a ser processado.
    """
    try:
        # Carrega o CSV em um DataFrame
        df = pd.read_csv(csv_file)
        print("Dados carregados:")
        print(df.head())

        # Tratamento dos dados
        # Converte a coluna "Data" para datetime
        df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

        # Converte a coluna "Preço" para float, lidando com "Indisponível"
        df["Preço"] = df["Preço"].apply(
            lambda x: float(x.replace(",", ".")) if isinstance(x, str) and x.replace(",", ".").replace(".", "", 1).isdigit() else None
        )

        # Remove linhas com preço nulo (se necessário)
        df = df.dropna(subset=["Preço"])

        # Exemplo de análise: Média de preço por marca
        avg_price = df.groupby("Nome")["Preço"].mean().reset_index()
        print("\nMédia de preço por placa:")
        print(avg_price)

        # Cria um gráfico de linha: Preço ao longo do tempo por marca
        fig = px.line(df, x="Data", y="Preço", color="Marca", 
                      title="Preço das Placas de Vídeo ao Longo do Tempo",
                      labels={"Preço": "Preço (R$)", "Data": "Data"})
        fig.show()

        # Cria um gráfico de barras: Média de preço por placa
        fig_bar = px.bar(avg_price, x="Nome", y="Preço", 
                         title="Média de Preço por Nome",
                         labels={"Preço": "Preço Médio (R$)"},
                         color="Nome")
        fig_bar.show()

    except Exception as e:
        print(f"Erro ao processar os dados: {e}")

# Permite executar o script diretamente, se desejar
if __name__ == "__main__":
    process_data()
