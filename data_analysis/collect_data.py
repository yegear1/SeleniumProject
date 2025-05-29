import requests
import json
import re
from datetime import datetime
import pandas as pd
import os
import csv

#url = "https://bestvaluegpu.com/_next/data/qUyCEpFqNx_bdUOLJ_peB/en-us/history/new-and-used-rtx-3070-price-history-and-specs.json?slug=new-and-used-rtx-3070-price-history-and-specs"

# Dicionário para mapear nomes de meses para números
MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

name = "3080"

url = f"https://bestvaluegpu.com/_next/data/qUyCEpFqNx_bdUOLJ_peB/en-us/history/new-and-used-rtx-{name}-price-history-and-specs.json?slug=new-and-used-rtx-{name}-price-history-and-specs"


def collect_data():
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        prices = data["pageProps"]["last12MonthsChart"]

        price_data = [
            [f"{entry['year']}-{MONTH_MAP[entry['month']]}-01", float(entry["used"]), float(entry["new"])]
            for entry in prices
        ]

        try:
            # 1. Carregar o arquivo CSV original
            df = pd.DataFrame(price_data, columns=['date', 'used', 'new'])

            # 2. Selecionar as colunas de interesse ('date' e 'new')
            df_transformado = df[['date', 'new']].copy()

            df_transformado.insert(0, 'Modelo', name)

            # 5. Exibir o resultado da transformação
            print("--- DataFrame Transformado ---")
            print(df_transformado.head())
        except Exception as e:
            print(f"Falhou em tratar os dados: {e}")

        try:
            nome_arquivo_saida = 'gpu_data.csv'
            df_transformado.to_csv(
                nome_arquivo_saida,
                mode='a',
                header=False,  # Não escreve a linha de cabeçalho (Modelo, date, Preco)
                index=False    # Não escreve o índice da linha (0, 1, 2...)
            )
        except Exception as e:
            print(f"Falhou em salvar os dados: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao coletar o JSON: {e}")
    except KeyError as e:
        print(f"Erro ao acessar os dados no JSON: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

collect_data()