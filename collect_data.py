import requests
import json
import time
from datetime import datetime
import csv

url = "https://bestvaluegpu.com/_next/data/6OhRjw5XtXNM9K1DF4VuS/en-us/history/new-and-used-rtx-3080-price-history-and-specs.json?slug=new-and-used-rtx-3080-price-history-and-specs"

# Dicionário para mapear nomes de meses para números
MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

def collect_data():
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Extrair a lista de preços dos últimos 12 meses
        prices = data["pageProps"]["last12MonthsChart"]
        #msrp = price["pageProps"]["same"]

        # Converter para formato [date, used, new]
        price_data = [
            [f"{entry['year']}-{MONTH_MAP[entry['month']]}-01", float(entry["used"]), float(entry["new"])]
            for entry in prices
        ]

        # Salvar em um arquivo CSV com timestamp no nome
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'rtx_3080_price_history_{timestamp}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'used', 'new'])  # Ajustar cabeçalhos
            for date, used, new in price_data:
                writer.writerow([date, used, new])

        print(f"Dados salvos em {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao coletar o JSON: {e}")
    except KeyError as e:
        print(f"Erro ao acessar os dados no JSON: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Executar a coleta
print(f"Coletando dados em {datetime.now()}")
collect_data()