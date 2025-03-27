from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

import time

def scrape_terabyte(driver):
    time.sleep(1)
    driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, 100);")
    time.sleep(2)

    try:
        close_modal = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='bannerPop']/div/div/button/span"))
        )
        close_modal.click()

    except:
        print("Erro em fechar o modal de promoções")

    time.sleep(2)

    try:
        close_push = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/div[1]/div/div[2]/button[1]"))
        )
        close_push.click()

    except:
        print("Erro em fechar o alerta de notificações")

    current_date = datetime.now().strftime("%d/%m/%Y")

    gpu_data = []
    product_grids = driver.find_elements(By.XPATH, '//*[@id="prodarea"]/div[1]/div')

    for grid in product_grids:
        try:
            try:
                grid.find_element(By.XPATH, './/div[contains(@class, "tbt_esgotado")]')
                continue
            except:
                pass

            price_element = grid.find_element(By.XPATH, './div/div[2]/div/div[4]/div[1]/div[2]/span')
            price_text = price_element.text.strip()
            price = price_text.replace("R$", "").replace("à vista", "").strip()

            name_element = grid.find_element(By.XPATH, './div/div[2]/div/div[2]/a/h2')
            full_name = name_element.text.lower()

            if "placa de vídeo" in full_name:
                name_part = full_name.replace("placa de vídeo", "").strip()
                name_part = name_part.split(",", 1)[0].strip()
            else:
                name_part = full_name.split(",", 1)[0].strip()

            parts = name_part.split(" ", 1)
            brand = parts[0] if len(parts) > 0 else "Desconhecida"
            name = parts[1] if len(parts) > 1 else name_part

            gpu_data.append({"Marca": brand, "Nome": name, "Preço": price, "Data": current_date})

        except Exception as e:
            print(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    time.sleep(1)
    driver.execute_script("window.scrollTo(100, 500);")

    return gpu_data