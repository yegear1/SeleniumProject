from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte
from selenium_stealth import stealth

import time
import psycopg2
import logging
import os
import tempfile

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Iniciando o script main.py")
time.sleep(5)


def create_driver():
    logger.info("Criando driver do Selenium...")
    options = Options()
    
    user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
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

logger.info("Iniciando loop principal...")
while True:
    driver = None
    try:
        driver = create_driver()
        time.sleep(10)
    
        gpu_data = []
        logger.info("Iniciando scraping na Terabyte...")
        gpu_data.extend(scrape_terabyte(driver)) # Puxa a lista da função scrape_terabyte
        logger.info("Scraping na Terabyte concluído.")

        driver.quit()

    except Exception as e:
        if driver:
            driver.quit()
        logger.exception("Erro ao criar o driver")  # mostra stacktrace
        continue

    try:
        logger.info("Conectando ao PostgreSQL...")
        conn = psycopg2.connect(
          dbname=os.getenv("POSTGRES_DB", "gpus_db"),
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
                    "INSERT INTO gpu_info (website, marca, nome) VALUES (%s, %s, %s) RETURNING id",
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
        logger.info(f"Dados salvos no PostgreSQL com {new_entries} novas entradas.")

        try:
            gpu_data = []
            print("gpu_data limpa")
        except:
            print("gpu_data falhou em ser limpa")
            continue

    except Exception as e:
        logger.info(f"Erro ao conectar ou salvar no PostgreSQL: {e}.")
        
    
    time.sleep(43200)

    logger.info("\nEXECUTANDO DENOVO O SCRIPT\n")
