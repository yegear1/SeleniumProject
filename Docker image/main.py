from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte
from selenium_stealth import stealth

import time
import csv
import psycopg2


# Declarações para o navegador parecer mais humano
options = Options()

def create_driver():
    user_data_dir = os.getenv("USER_DATA_DIR", "/tmp/user_data")

    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--headless")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Erro ao criar o driver com WebDriver Manager: {e}")
        driver = webdriver.Chrome(options=options)

    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )
    return driver

time.sleep(5)

while True:
    try:
        driver = create_driver()
        time.sleep(10)
        
        gpu_data = []
        gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte
        print("Scraping na terabyte concluído.")

        driver.quit()

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        continue

    try:
        with open("gpu_data.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["Site", "Marca", "Nome", "Preço", "Data"])
            writer.writerows(gpu_data)
        print(f"Dados salvos em gpu_data.csv com {len(gpu_data)} entradas.")
    except Exception as e:
        print(f"Erro ao salvar no CSV: {e}")

    #Conexão com o banco
    try:
        conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "gpu_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "192.168.18.235"),
        port=os.getenv("POSTGRES_PORT", "5432")
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
                    "INSERT INTO gpu_info (site, marca, nome) VALUES (%s, %s, %s) RETURNING id",
                    (entry["Site"],entry["Marca"], entry["Nome"])
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

        try:
            gpu_data = []
            print("gpu_data limpa")
        except:
            print("gpu_data falhou em ser limpa")
            continue

    except Exception as e:
        print(f"Erro ao conectar ou salvar no PostgreSQL: {e}")
    
    time.sleep(43200)

    print("\n EXECUTANDO DENOVO O SCRIPT \n")
