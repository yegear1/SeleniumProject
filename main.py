from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import csv
import time

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # Remove sinal de automação
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")  # User-agent real
options.add_argument("user-data-dir=C:\\Users\\Y\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--profile-directory=Profile 1")

driver = webdriver.Chrome(options=options)

gpu_data = []

time.sleep(1)

driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")

time.sleep(2)

product_grids = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="prodarea"]/div[1]/div')))

driver.execute_script("window.scrollTo(0, 500);")

time.sleep(1)

try:
    close_modal = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='bannerPop']/div/div/button/span"))
    )
    close_modal.click()

    close_push = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/div[1]/div/div[2]/button[1]"))
    )
    close_push.click()

except:
    print("Erro no try/expect 1")

for grid in product_grids:
    try:
        name_element = grid.find_element(By.XPATH, './div/div[2]/div/div[2]/a/h2')
        full_name = name_element.text.lower()

        if "placa de vídeo" in full_name:
            name_part = full_name.replace("placa de vídeo", "").strip()

            name_part = name_part.split(",", 1)[0].strip()
        else:
            name_part = full_name.split(",", 1)[0].strip()

        driver.execute_script("window.scrollTo(0, 10);")

        parts = name_part.split(" ", 1)
        brand = parts[0] if len(parts) > 0 else "Desconhecida"
        name = parts[1] if len(parts) > 1 else name_part

        # Adiciona à lista
        gpu_data.append({"Marca": brand, "Nome": name})
    except Exception as e:
        print(f"Erro ao extrair um produto: {e}")
        continue

# Salva em CSV
with open("gpu_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Marca", "Nome"])
    writer.writeheader()
    writer.writerows(gpu_data)


driver.quit()

print(f"Dados salvos em gpu_data.csv com {len(gpu_data)} entradas.")
