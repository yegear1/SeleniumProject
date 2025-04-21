from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.blocking import BlockingScheduler
from logging.handlers import RotatingFileHandler
from datetime import datetime

from scrapers import scrape_terabyte, scrape_pichau, scrape_kabum
from utils import create_driver, save_csv, connect_db

import logging
import time
import os

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.propagate = False

# Formato dos logs
log_formatter = logging.Formatter('%(levelname)s - %(message)s')

# Manipulador para o terminal (console)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
console_handler.encoding = 'utf-8'  # Tentar forçar UTF-8 no terminal
logger.addHandler(console_handler)

# Criar a pasta logs se ela não existir
os.makedirs("logs", exist_ok=True)

# Manipulador para o arquivo (salvar logs em um arquivo)
log_filename = f"logs/scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

scheduler = BlockingScheduler(timezone='America/Sao_Paulo')
current_date = datetime.now().strftime("%Y-%m-%d")

site_counters = {
    "terabyte": {"total_gpu": 0, "num_gpu": 0},
    "pichau": {"total_gpu": 0, "num_gpu": 0},
    "kabum": {"total_gpu": 0, "num_gpu": 0},
}

def scrape_task():
    logger.info("\n\nIniciando a função scrape_task\n\n")

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
        logger.exception("Erro ao criar o driver")  # mostra stacktrace

    try:
        for site, counts in site_counters.items():
            logger.info(f"Site {site}: {counts['total_gpu']} coletadas, {counts['num_gpu']} salvas")

        #connect_db(gpu_data)
        #save_csv(gpu_data)
        gpu_data.clear()
        logger.info("gpu_data limpa")

    except Exception as e:
        logger.error(f"Erro ao salvar no banco: {e}")
    
    file_handler.close()
    logger.removeHandler(file_handler)

#scheduler.add_job(scrape_task, 'cron', hour=12, minute=0)
#scheduler.add_job(scrape_task, 'cron', hour=16, minute=0)
#scheduler.add_job(scrape_task, 'cron', hour=20, minute=0)

logger.info("\n\nIniciando o script main.py\n\n")
scrape_task()

#try:
#    scheduler.start()
#except (KeyboardInterrupt, SystemExit):
#    logger.info("\n\nScript finalizado pelo usuário\n\n")
#    scheduler.shutdown(wait=False)  # Força o encerramento do agendador
    