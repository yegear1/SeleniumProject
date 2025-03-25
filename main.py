from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import time

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # Remove sinal de automação
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove switch de automação
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")  # User-agent real
options.add_argument("user-data-dir=/caminho/para/seu/perfil")


driver = webdriver.Chrome(options=options)


driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")

time.sleep(2)

driver.execute_script("window.scrollTo(0, 500);")

# Espera e fecha o modal (se existir)
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


input("Pressione Enter para fechar o navegador...")
driver.quit()
