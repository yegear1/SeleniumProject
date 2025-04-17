from selenium.webdriver.support import expected_conditions as EC

from scrapers import scrape_terabyte, scrape_pichau

from utils import create_driver, save_csv, connect_db

import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Iniciando o script main.py")
time.sleep(5)

logger.info("Iniciando loop principal...")
while True:
    driver = None
    try:
        driver = create_driver()
        time.sleep(10)
    
        gpu_data = []
  
        gpu_data.extend(scrape_terabyte(driver))

        gpu_data.extend(scrape_pichau(driver))

        driver.quit()

    except Exception as e:
        if driver:
            driver.quit()
        logger.exception("Erro ao criar o driver")  # mostra stacktrace
        continue

    connect_db(gpu_data)

    gpu_data.clear()
    logger.info("gpu_data limpa")

    time.sleep(43200)

    logger.info("\nEXECUTANDO DENOVO O SCRIPT\n")
