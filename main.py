from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

from scrapers import scrape_terabyte, scrape_pichau, scrape_kabum
from utils import create_driver, save_csv, connect_db

import logging
import logging.handlers
import time
import os

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.propagate = False

log_formatter = logging.Formatter('%(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

os.makedirs("logs", exist_ok=True)

num=1
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=f"logs/scraping_{num}.log",
    when='D',
    interval=1,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

site_counters = {
    "terabyte": {"total_gpu": 0, "num_gpu": 0},
    "pichau": {"total_gpu": 0, "num_gpu": 0},
    "kabum": {"total_gpu": 0, "num_gpu": 0},
}

def scrape_task():
    current_date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"\n\nIniciando a função scrape_task em {datetime.now()}\n")

    for site in site_counters:
        site_counters[site]["total_gpu"] = 0
        site_counters[site]["num_gpu"] = 0

    driver = None
    gpu_data = []
    try:
        driver = create_driver()
        time.sleep(2)
        driver.get("https://www.google.com/")
        time.sleep(1)
  
        gpu_data.extend(scrape_terabyte(driver, current_date, counters=site_counters))        
        #gpu_data.extend(scrape_pichau(driver, current_date, counters=site_counters))
        #gpu_data.extend(scrape_kabum(driver, current_date, counters=site_counters))

        driver.quit()

    except Exception as e:
        if driver:
            driver.quit()
        logger.exception("Erro ao criar o driver") 

    try:
        for site, counts in site_counters.items():
            logger.info(f"Site {site}: {counts['total_gpu']} coletadas, {counts['num_gpu']} salvas")

        #connect_db(gpu_data)
        save_csv(gpu_data)
        gpu_data.clear()
        logger.info("gpu_data limpa")

    except Exception as e:
        logger.error(f"Erro ao salvar no banco: {e}")

logger.info(f"\n\nIniciando o script main.py em {datetime.now()}\n")

while True:
    scrape_task()
    num+=1
    time.sleep(1)
