from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

from utils import normalize_gpu_name, normalize_price, connect_db

import time
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_terabyte(driver):
    logger.info("Iniciando scraping na Terabyte...")
    time.sleep(5)

    try:
        driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "prodarea")))
        logger.info("Site totalmente carregado, prosseguindo com a raspagem")
    except TimeoutException:
        logger.info("Tempo esgotado ao esperar pelo elemento 'prodarea'. Retornando lista vazia.")
        return []

    time.sleep(2)

    driver.execute_script("window.scrollTo(0, 100);")

    time.sleep(2)

    try:
        close_modal = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='bannerPop']/div/div/button/span"))
        )
        close_modal.click()
        logger.info("Modal de promos fechado")

    except:
        logger.info("Erro em fechar o modal de promoções")

    time.sleep(2)

    try:
        close_push = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/div[1]/div/div[2]/button[1]"))
        )
        close_push.click()

    except:
        print("Erro em fechar o alerta de notificações")

    current_date = datetime.now().strftime("%Y/%m/%d")

    gpu_data = []
    product_grids = driver.find_elements(By.XPATH, '//*[@id="prodarea"]/div[1]/div')

    for grid in product_grids:
        try:
            try:
                grid.find_element(By.XPATH, './/div[contains(@class, "tbt_esgotado")]')
                continue
            except:
                pass
            
            try:
                price_element = grid.find_element(By.XPATH, './div/div[2]/div/div[4]/div[1]/div[2]/span')
            except:
                logger.info("Erro ao coletar o preço")
                continue

            price = normalize_price(price_element)

            try:
                name_element = grid.find_element(By.XPATH, './div/div[2]/div/div[2]/a/h2').text
            except:
                logger.info("Erro ao coletar o nome")
                continue

            brand_gpu, name_gpu = normalize_gpu_name(name_element)

            if brand_gpu is not None:
                gpu_data.append({
                    "Site": "terabyte",
                    "Marca": brand_gpu,
                    "Nome": name_gpu,
                    "Preço": price,
                    "Data": current_date,
                })
            else:
                continue

        except Exception as e:
            logger.info(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    time.sleep(2)
    driver.get("https://www.google.com")
    driver.execute_script("window.scrollTo(0, 500);")
    logger.info("Scraping na Terabyte concluído.")
    return gpu_data

def scrape_pichau(driver):
    time.sleep(5)
   
    try:
        logger.info("Iniciando o scrapping na pichau")
        driver.get("https://www.pichau.com.br/hardware/placa-de-video")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div[3]")))
        logger.info("Site totalmente carregado, prosseguindo com a raspagem")
    except TimeoutException:
        logger.error("Tempo esgotado ao esperar pelo elemento 'scroll-subcategories'. Retornando lista vazia.")
        return []

    try:
        last_page = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/nav/ul/li[8]/button'))
        )
        aria_label = last_page.get_attribute("aria-label")
        page_count = int(re.search(r'\d+', aria_label).group())
        logger.info(f"Número total de páginas: {page_count}")
    except Exception as e:
        logger.error(f"Erro ao coletar o número de páginas: {e}")
        page_count = 1

    time.sleep(2)

    driver.execute_script("window.scrollTo(0, 100);")

    time.sleep(2)

    current_date = datetime.now().strftime("%Y/%m/%d")
    gpu_data = []
    current_page = 1
    while current_page <= page_count:

        logger.info(f"Acessando página {current_page}...")
        time.sleep(2)

        # Encontrar os produtos (ajuste o seletor conforme o HTML do site)
        products_grid = driver.find_elements(By.CLASS_NAME, "mui-p3mq1s") 

        for grid in products_grid:
            try:
                try:
                    grid.find_element(By.CLASS_NAME, 'mui-8rpawh-out_of_stock')
                    continue
                except:
                    pass

                try:
                    name_element = grid.find_element(By.CLASS_NAME, "mui-1jecgbd-product_info_title-noMarginBottom").text
                except:
                    logger.info("Erro ao coletar o nome")
                    continue

                try:
                    price_element = grid.find_element(By.CLASS_NAME, "mui-1q2ojdg-price_vista")
                except:
                    logger.info("Erro ao coletar o preço")
                    continue
                
                price = normalize_price(price_element)

                brand_gpu, name_gpu = normalize_gpu_name(name_element)


                if brand_gpu is not None:
                    gpu_data.append({
                        "Site": "pichau",
                        "Marca": brand_gpu,
                        "Nome": name_gpu,
                        "Preço": price,
                        "Data": current_date,
                    })
                else:
                    continue


            except Exception as e:
                print(f"Erro ao processar produto na página {current_page}: {e}")
                continue

        if current_page < page_count:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "next page")]'))
                )
                next_button.click()
                time.sleep(5)  # Aguarda o carregamento da próxima página
                driver.execute_script("window.scrollTo(0, 100);")
                current_page += 1
            except Exception as e:
                logger.error(f"Erro ao passar para a próxima página: {e}")
                break
        else:
            break

    logger.info("Scraping na Pichau concluído.")
    return gpu_data
