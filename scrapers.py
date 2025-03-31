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
        "1050 ti",
        "1060",
        "1070",
        "1070 ti",
        "1080",
        "1080 ti",
        "1650",
        "1650 super",
        "1660",
        "1660 super",
        "1660 ti",
        "2060",
        "2060 super",
        "2070",
        "2070 super",
        "2080",
        "2080 super",
        "2080 ti",
        "3050",
        "3060",
        "3060 ti",
        "3070",
        "3070 ti",
        "3080",
        "3080 ti",
        "3090",
        "3090 ti",
        "4050",
        "4060",
        "4060 ti",
        "4070",
        "4070 super",
        "4070 ti",
        "4070 ti super",
        "4080",
        "4080 super",
        "4090",
        "4090 ti",
        "5060",
        "5070",
        "5070 super",
        "5070 ti",
        "5080",
        "5090"
    ],
    "RX": [
        "550",
        "560",
        "570",
        "580",
        "580 xt",
        "590",
        "590 xt",
        "6600",
        "6600 xt",
        "6650",
        "6650 xt",
        "6700",
        "6700 xt",
        "6800",
        "6800 xt",
        "6900",
        "6900 xt",
        "7600",
        "7600 xt",
        "7700",
        "7700 xt",
        "7800",
        "7800 xt",
        "7900",
        "7900 xt",
        "7900 xtx"
    ],
    "ARC": [
        "a380",
        "a580",
        "a750",
        "a770",
        "b580"
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
        padrao = re.compile(f"{line.lower()}\\s*(\\d+\\s*(ti|super|xt|xtx|ti super)?)", re.IGNORECASE)
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
    
    if result['brand'] and result['gpu_model']:
        brand_gpu = result['brand'][0]
        name_gpu = result['gpu_model'][0]

        print(f"{brand_gpu}")
        print(f"{name_gpu}")
    else:
        brand_gpu = None
        name_gpu = None
        print(f"Produto ignorado: Marca ou modelo não encontrados em '{full_name}'")

    return brand_gpu, name_gpu

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
    site = "terabyte"
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
                name_element = grid.find_element(By.XPATH, './div/div[2]/div/div[2]/a/h2')
            except:
                print("Erro em coletar o nome")
                continue

            full_name = name_element.text
                
            brand_gpu, name_gpu = normalize_gpu_name(full_name)

            if brand_gpu is not None:
                gpu_data.append({
                    "Site": site,
                    "Marca": brand_gpu,
                    "Nome": name_gpu,
                    "Preço": price,
                    "Data": current_date,
                })
            else:
                continue

        except Exception as e:
            print(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    time.sleep(2)
    driver.get("https://www.google.com")
    driver.execute_script("window.scrollTo(0, 500);")
    return gpu_data
