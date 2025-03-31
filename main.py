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
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")  # User-agent real
options.add_argument("user-data-dir=C:\\Users\\Y\\AppData\\Local\\Google\\Chrome\\User Data") # Adiciona um caminho para o user-data
options.add_argument("--disable-blink-features=AutomationControlled")  # Remove sinal de automação
options.add_argument("--profile-directory=Profile 1") # Adiciona um perfil
options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória
options.add_argument("--disable-extensions")
options.add_argument("--start-maximized")
options.add_argument("--lang=pt-BR")
options.add_argument("--no-sandbox")  # Necessário em alguns sistemas
options.add_argument("--headless")  # Executa sem interface gráfica



options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação


driver = webdriver.Chrome(options=options) 

time.sleep(3)

gpu_data = []

driver.get("https://www.google.com")

time.sleep(1)

gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte

with open("gpu_data.csv", "a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Site","Marca", "Nome", "Preço", "Data"])
    #writer.writeheader()
    writer.writerows(gpu_data)

driver.quit()

print(f"Dados salvos em gpu_data.csv com {len(gpu_data)} entradas.")
