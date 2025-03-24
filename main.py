from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome()


driver.get("https://www.terabyteshop.com.br/hardware/placas-de-video")

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


input("Pressione Enter para fechar o navegador...")//*[@id="submitFormContinuar"]
driver.quit()
