from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte

import time
import csv
import psycopg2


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
#options.add_argument("--headless")  # Executa sem interface gráfica

options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação

driver = webdriver.Chrome(options=options) 

time.sleep(5)

gpu_data = []

driver.get("https://www.google.com")

time.sleep(2)

gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte

with open("gpu_data.csv", "a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Site","Marca", "Nome", "Preço", "Data"])
    writer.writerows(gpu_data)

driver.quit()

print(f"Dados salvos em gpu_data.csv com {len(gpu_data)} entradas.")


#Conecao com o banco
try:
    conn = psycopg2.connect(
        dbname="gpus",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    new_entries = 0
    for entry in gpu_data:
        # Verifica se a placa já existe em gpu_info
        cursor.execute(
            "SELECT id FROM gpu_info WHERE marca = %s AND nome = %s",
            (entry["Marca"], entry["Nome"])
        )
        result = cursor.fetchone()

        if result:
            gpu_id = result[0]
        else:
            # Insere a nova placa
            cursor.execute(
                "INSERT INTO gpu_info (marca, nome) VALUES (%s, %s) RETURNING id",
                (entry["Marca"], entry["Nome"])
            )
            gpu_id = cursor.fetchone()[0]

        # Verifica se já existe um preço para essa placa na mesma data
        cursor.execute(
            "SELECT 1 FROM gpu_prices WHERE gpu_id = %s AND data = %s",
            (gpu_id, entry["Data"])
        )
        if cursor.fetchone():
            continue  # Pula se já existe

        # Insere o preço e a data
        cursor.execute(
            "INSERT INTO gpu_prices (gpu_id, preco, data) VALUES (%s, %s, %s)",
            (gpu_id, entry["Preço"], entry["Data"])
        )
        new_entries += 1

    # Commit e fecha a conexão
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Dados salvos no PostgreSQL com {new_entries} novas entradas.")

except Exception as e:
    print(f"Erro ao conectar ou salvar no PostgreSQL: {e}")