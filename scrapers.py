from selenium.webdriver.common.by import By
import time

def scrape_terabyte(driver):
    time.sleep(3)
    driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")
    time.sleep(3)

    gpu_data = []
    product_grids = driver.find_elements(By.XPATH, '//*[@id="prodarea"]/div[1]/div')

    for grid in product_grids:
        try:
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

            driver.execute_script("window.scrollTo(0, 10);")

            parts = name_part.split(" ", 1)
            brand = parts[0] if len(parts) > 0 else "Desconhecida"
            name = parts[1] if len(parts) > 1 else name_part

            gpu_data.append({"Marca": brand, "Nome": name, "Preço": price})
            
        except Exception as e:
            print(f"Erro ao extrair um produto da Terabyte: {e}")
            continue

    return gpu_data