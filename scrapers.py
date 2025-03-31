from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

import time
import re
import json

def normalize_gpu_name(name_element):
    known_gpus = '''
    {
    "RTX": [
    "1050",
    "1060",
    "2050",
    "2060",
    "3060",
    "3070",
    "3080",
    "3090",
    "4050",
    "4060",
    "4070 ti",
    "4080",
    "4090",
    "5090"
    ],
    "RX": [
    "550",
    "560",
    "570",
    "580",
    "590",
    "6600",
    "6700",
    "6800",
    "6900",
    "7600",
    "7700",
    "7800",
    "7900"
    ]
    }
    '''

    known_brands = '''
    {
    "brand": [
    "ASUS",
    "MSI",
    "Gigabyte",
    "ZOTAC",
    "PNY",
    "EVGA",
    "Palit",
    "Galax",
    "Inno3D",
    "Colorful",
    "Sapphire",
    "PowerColor",
    "XFX",
    "ASRock",
    "HIS",
    "VisionTek",
    "AFOX",
    "Sparkle"
    ]
    }
    '''
    gpu_list = json.loads(known_gpus)
    brand_list = json.loads(known_brands)

    result = {
        "gpu_model": [],
        "brand": []
    }

    full_name = name_element.lower()

    # Identificar modelos de GPU (RTX e RX)
    for line in ["RTX", "RX"]:
        # Padrão para capturar números e sufixos como "TI" ou "Super"
        padrao = re.compile(f"{line.lower()}\\s*(\\d+\\s*(ti|super)?)", re.IGNORECASE)
        matches = padrao.findall(full_name)
        
        for match in matches:
            modelo = match[0].strip()  # Captura o modelo completo, ex: "4070 ti"
            if modelo in gpu_list[line]:
                result["gpu_model"].append(f"{line} {modelo}")
    
    # Identificar marcas
    for brand in brand_list["brand"]:
        pattern = re.compile(re.escape(brand), re.IGNORECASE)
        if pattern.search(full_name):
            result["brand"].append(brand)

    return result  


def scrape_terabyte(driver):
    time.sleep(1)

    try:
        driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "prodarea")))
    except TimeoutException:
        print("Tempo esgotado ao esperar pelo elemento 'prodarea'. Retornando lista vazia.")
        return []

    time.sleep(2)

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
            
            try:
                price_element = grid.find_element(By.XPATH, './div/div[2]/div/div[4]/div[1]/div[2]/span')
            except:
                print("Erro em coletar o preço")
                continue
            
            price_text = price_element.text.strip()
            price = price_text.replace("R$", "").replace("à vista", "").strip()

            try:
                name_element = grid.find_element(By.XPATH, '//*[@id="prodarea"]/div[1]/div[2]/div/div[2]/div/div[2]/a')
            except:
                print("Erro em coletar o nome")
                continue

            full_name = name_element.textS
                
            gpu_info = normalize_gpu_name(full_name)

            marca = gpu_info['brand'][0]  # Pega o primeiro elemento da lista de marcas
            modelo = gpu_info['gpu_model'][0]  # Pega o primeiro elemento da lista de modelos
            gpu_data.append({
                "Marca": marca,
                "Nome": modelo,
                "Preço": price,
                "Data": current_date,
            })

        except Exception as e:
            print(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    time.sleep(2)
    driver.get("https://www.google.com")
    driver.execute_script("window.scrollTo(0, 500);")
