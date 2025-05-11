import requests
import json
import time
from datetime import datetime
import csv

url = "https://placasdevideo.com/_next/data/X9FHI2E3tRmnB-X2WkNdw/pt-BR/placa-de-video/kabum/placa-de-video-asrock-amd-radeon-rx-6600-cld-8g-8gb-90-ga2rzz-00uanf.json"

def collect_data():
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        prices = data["pageProps"]["data"]["prices"]

        price_data = [
            [entry["date"][:10], float(entry["price"])]
            for entry in prices
        ]

# Salvar em um arquivo CSV com timestamp no nome
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'precos_rx6600_kabum_{timestamp}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['data', 'preco'])
            for date, price in price_data:
                writer.writerow([date, price])

        print(f"Dados salvos em {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao coletar o JSON: {e}")


print(f"Coletando dados em {datetime.now()}")
collect_data()
