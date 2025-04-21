from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from selenium_stealth import stealth

import re
import os
import csv
import json
import logging
import tempfile
import psycopg2


logger = logging.getLogger("main")


def create_driver():
    logger.info("Criando driver do Selenium...")
    options = Options()
    options.add_argument("--start-maximized")
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")

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
        "5060 ti",
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
        "7900 xtx",
        "9070",
        "9070 xt"
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
    "AERO",
    "EAGLEOC",
    "MSI",
    "Gigabyte",
    "ZOTAC",
    "PNY",
    "EVGA",
    "PALIT",
    "GALAX",
    "Inno3D",
    "Colorful",
    "Sapphire",
    "PowerColor",
    "PCYES!",
    "PCYES",
    "XFX",
    "ASROCK",
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
        
        
        logger.info(f"{brand_gpu}")
        logger.info(f"{name_gpu}")
    else:
        brand_gpu = None
        name_gpu = None
        logger.info(f"Produto ignorado: Marca ou modelo não encontrados em '{full_name}'")

    return brand_gpu, name_gpu

def normalize_price(price_element):
    price_text = price_element.text.strip()
    price = price_text.replace("R$", "").replace("à vista", "").replace(".", "").replace(",", ".").strip()
    return float(price)

def connect_db(gpu_data):
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
            cursor.execute(
                "SELECT id FROM website_id WHERE name = %s",
                (entry["Site"],)
            )
            website_result = cursor.fetchone()
            if not website_result:
                # Se o site não existe, insere na tabela website_id
                cursor.execute(
                    "INSERT INTO website_id (name) VALUES (%s) RETURNING id",
                    (entry["Site"],)
                )
                website_result = cursor.fetchone()
                if website_result is None:
                    raise ValueError(f"Falha ao inserir site {entry['Site']} em website_id")
                website_id = website_result[0]
            else:
                website_id = website_result[0]

            # Verifica se a placa já existe em gpu_info
            cursor.execute(
                "SELECT id FROM gpu_info WHERE marca = %s AND nome = %s",
                (entry["Marca"], entry["Nome"])
            )
            gpu_result = cursor.fetchone()

            if gpu_result:
                gpu_id = gpu_result[0]
            else:
                # Insere a nova placa
                cursor.execute(
                    "INSERT INTO gpu_info (marca, nome) VALUES (%s, %s) RETURNING id",
                    (entry["Marca"], entry["Nome"])
                )
                gpu_result = cursor.fetchone()
                if gpu_result is None:
                    raise ValueError(f"Falha ao inserir GPU {entry['Marca']} {entry['Nome']} em gpu_info")
                gpu_id = gpu_result[0]

            # Verifica se já existe um preço para essa placa na mesma data
            cursor.execute(
                "SELECT 1 FROM gpu_prices WHERE gpu_id = %s AND website_id = %s AND data = %s",
                (gpu_id, website_id, entry["Data"])
            )
            if cursor.fetchone():
                continue  # Pula se já existe

            # Insere o preço e a data
            cursor.execute(
                "INSERT INTO gpu_prices (gpu_id, website_id, preco, data) VALUES (%s, %s, %s, %s)",
                (gpu_id, website_id, entry["Preço"], entry["Data"])
            )
            new_entries += 1

    # Commit e fecha a conexão
        conn.commit()
        logger.info(f"Dados salvos no PostgreSQL com {new_entries} novas entradas.")

    except Exception as e:
        logger.info(f"Erro ao conectar ou salvar no PostgreSQL: {e}.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_csv(gpu_data):
    with open("gpu_data.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Site", "Marca", "Nome", "Preço", "Data"])
        writer.writeheader()
        writer.writerows(gpu_data)
    logger.info("Salvo em gpu_data")
