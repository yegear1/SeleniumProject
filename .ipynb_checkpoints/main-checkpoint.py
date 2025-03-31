from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte

import time
import csv
import os
import json

# Declarações para o navegador parecer mais humano
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # Remove sinal de automação
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")  # User-agent real
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--lang=pt-BR")
options.add_argument("user-data-dir=C:\\Users\\Y\\AppData\\Local\\Google\\Chrome\\User Data") # Adiciona um caminho para o user-data
options.add_argument("--profile-directory=Profile 1") # Adiciona um perfil

driver = webdriver.Chrome(options=options) 

time.sleep(5)

gpu_data = []
#gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte

with open("known_gpus.json", "r", encoding="utf-8") as f:
    known_gpus = json.load(f)

rtx_models = known_gpus["RTX"]
print(rtx_models)

with open("gpu_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Marca", "Nome", "Preço", "Data"])
    writer.writeheader()
    writer.writerows(gpu_data)

driver.quit()

print(f"Dados salvos em gpu_data.csv com {len(gpu_data)} entradas.")
