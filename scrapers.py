from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from utils import normalize_gpu_name, normalize_price

import time
import re
import logging

logger = logging.getLogger("main")

def wait_load(driver,grid_name):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, grid_name)))
        logger.info("Placas carregadas, proseguindo com raspagem")
    except TimeoutException:
        logger.error(f"Tempo esgotado ao esperar pelo elemento '{grid_name}'. Retornando lista vazia.")

def scrape_terabyte(driver, current_date, site="terabyte", counters=None):
    logger.info("\n\nIniciando scraping na Terabyte\n\n")
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
        logger.info("Erro em fechar o alerta de notificações")

    gpu_data = []

    product_grids = driver.find_elements(By.XPATH, '//*[@id="prodarea"]/div[1]/div')

    for grid in product_grids:
        try:
            try:
                grid.find_element(By.XPATH, './/div[contains(@class, "tbt_esgotado")]')
                logger.info(f"Produto esgotado")
                break
            except:
                pass
            
            try:
                price_element = grid.find_element(By.XPATH, './div/div[2]/div/div[4]/div[1]/div[2]/span')
            except:
                logger.error("Erro ao coletar o preço")
                continue

            try:
                name_element = grid.find_element(By.XPATH, './div/div[2]/div/div[2]/a/h2').text
            except:
                logger.error("Erro ao coletar o nome")
                continue
            
            price = normalize_price(price_element.text)
            brand_gpu, name_gpu = normalize_gpu_name(name_element)

            counters[site]["total_gpu"] += 1

            if brand_gpu is not None:
                gpu_data.append({
                    "Fonte": "terabyte",
                    "Marca": brand_gpu,
                    "Nome": name_gpu,
                    "Preço": price,
                    "Data": current_date,
                })
                counters[site]["num_gpu"] += 1
            else:
                continue

        except Exception as e:
            logger.error(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    time.sleep(2)
    driver.get("https://www.google.com")
    logger.info(f"\n\nForam coletadas {counters[site]['total_gpu']} placas no site {site}")
    logger.info(f"Mas somente {counters[site]['num_gpu']} foram salvas")    
    logger.info("Scraping na terabyte concluido\n\n")
    return gpu_data

def scrape_pichau(driver, current_date, site="pichau", counters=None):
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
        logger.info(f"==== Número total de páginas: {page_count} ====")
    except Exception as e:
        logger.error(f"Erro ao coletar o número de páginas: {e}")
        page_count = 1

    time.sleep(2)

    driver.execute_script("window.scrollTo(0, 100);")

    time.sleep(2)

    current_page = 1

    gpu_data = []

    while current_page <= page_count:

        logger.info(f"== Acessando página {current_page} ==")
        time.sleep(2)

        # Encontrar os produtos (ajuste o seletor conforme o HTML do site)
        products_grid = driver.find_elements(By.CLASS_NAME, "mui-p3mq1s") 

        for grid in products_grid:
            try:
                try:
                    grid.find_element(By.CLASS_NAME, 'mui-8rpawh-out_of_stock')
                    logger.info(f"Produto esgotado")
                    break
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
                
                price = normalize_price(price_element.text)

                brand_gpu, name_gpu = normalize_gpu_name(name_element)

                counters[site]["total_gpu"] += 1

                if brand_gpu is not None:
                    gpu_data.append({
                        "Fonte": "pichau",
                        "Marca": brand_gpu,
                        "Nome": name_gpu,
                        "Preço": price,
                        "Data": current_date,
                    })
                    counters[site]["num_gpu"] += 1
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

    logger.info(f"\n\nForam coletadas {counters[site]['total_gpu']} placas no site {site}")
    logger.info(f"Mas somente {counters[site]['num_gpu']} foram salvas")      
    logger.info("Scraping na Pichau concluido\n\n")
    return gpu_data

def scrape_kabum(driver, current_date, site="kabum", counters=None):
    logger.info("\n\nIniciando o scrapping na Kabum\n\n")
    time.sleep(5)

    try:
        logger.info("Aguardando o carregamento do site Kabum...")
        driver.get("https://www.kabum.com.br/hardware/placa-de-video-vga")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ebKsig")))
        logger.info("Site totalmente carregado, prosseguindo com a raspagem")
    except TimeoutException as e:
        logger.error(f"Erro ao carregar o site Kabum: {e}")
        return []   
    
    try:
        last_page = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div[3]/div/div/div[2]/div/div[3]/ul/li[12]/a'))    
    )
        aria_label = last_page.get_attribute("aria-label")
        page_count = int(re.search(r'\d+', aria_label).group())
        logger.info(f"==== Número total de páginas: {page_count} ====")
    except Exception as e:
        logger.error(f"Erro ao coletar o número de páginas: {e}")
        page_count = 1

    gpu_data = []
    current_page = 1
    grid_name = "ebKsig"
    while current_page <= page_count:

        logger.info(f"Acessando página {current_page}...")

        wait_load(driver, grid_name)

        products_grid = driver.find_elements(By.CLASS_NAME, "productCard")

        for grid in products_grid:
            try:

                try:
                    name_element = grid.find_element(By.CLASS_NAME, "iJKRqI").text
                except Exception as e:
                    logger.info(f"Erro {e} ao coletar o nome")
                    continue

                try:
                    price_element = grid.find_element(By.CLASS_NAME, "priceCard")
                except Exception as e:
                    logger.info(f"Erro {e} ao coletar o preço")
                    continue
                
                
                driver.execute_script("window.scrollTo(0, 300);")

                price = normalize_price(price_element.text)
                
                time.sleep(1)

                brand_gpu, name_gpu = normalize_gpu_name(name_element)

                driver.execute_script("window.scrollTo(300, 0);")

                counters[site]["total_gpu"] += 1

                if brand_gpu is not None:
                    gpu_data.append({
                        "Fonte": "kabum",
                        "Marca": brand_gpu,
                        "Nome": name_gpu,
                        "Preço": price,
                        "Data": current_date,
                    })
                    counters[site]["num_gpu"] += 1
                else:
                    continue


            except Exception as e:
                print(f"Erro ao processar produto na página {current_page}: {e}")
                continue

        if current_page < page_count:
            try:
                next_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'nextLink'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)

                time.sleep(2)

                current_page += 1
            except Exception as e:
                logger.error(f"Erro ao passar para a próxima página: {e}")
                break

        else:
            break

    logger.info(f"\n\nForam coletadas {counters[site]['total_gpu']} placas no site {site}")
    logger.info(f"Mas somente {counters[site]['num_gpu']} foram salvas")      
    logger.info("Scraping na Kabum concluido\n\n")
    return gpu_data
