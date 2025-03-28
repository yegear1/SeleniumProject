from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte
from process_data import process_data

import time
import csv
import os
import json

# Declarações para o navegador parecer mais humano
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # Remove sinal de automação
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")  # User-agent real
options.add_argument("user-data-dir=C:\\Users\\Y\\AppData\\Local\\Google\\Chrome\\User Data") # Adiciona um caminho para o user-data
options.add_argument("--profile-directory=Profile 1") # Adiciona um perfil

driver = webdriver.Chrome(options=options) 

time.sleep(5)

gpu_data = []
gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte

try:
    with open("known_gpus.json", "r") as f:
        known_gpus = json.load(f)
except json.JSONDecodeError as e:
    print(f"Erro ao carregar known_gpus.json: {e}")

filtered_data = []
for entry in gpu_data:
    line = entry["Linha"]
    model = entry["Modelo"]
    if line in known_gpus and model in known_gpus[line]:
        filtered_data.append(entry)

csv_file = "gpu_data.csv"

existing_data = [] # Verifica se o CSV existe
if os.path.exists(csv_file):
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_data = list(reader)

existing_entries = {(entry["Marca"], entry["Nome"], entry["Preço"], entry["Data"]) for entry in existing_data}

# Se for a primeira vez ou houver novas entradas, escreve no CSV
new_entries = []

for entry in filtered_data:
    entry_tuple = (entry["Marca"], entry["Nome"], entry["Preço"], entry["Data"])
    if entry_tuple not in existing_entries:
        new_entries.append({
            "Marca": entry["Marca"],
            "Nome": entry["Nome"],
            "Preço": entry["Preço"],
            "Data": entry["Data"]
        })

if not existing_data:  # Se o arquivo não existia, cria e escreve o cabeçalho
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Marca", "Nome", "Preço", "Data"])
        writer.writeheader()
        writer.writerows(gpu_data)

else:  # Se o arquivo já existe, apenas adiciona as novas entradas
    if new_entries:  # Só escreve se houver novas entradas
        with open(csv_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Marca", "Nome", "Preço", "Data"])
            writer.writerows(new_entries)

time.sleep(2)

driver.execute_script("window.scrollTo(500, 700);")

driver.quit()

total_entries = len(existing_data) + len(new_entries)
print(f"Dados salvos em gpu_data.csv com {total_entries} entradas (novas: {len(new_entries)}).")
