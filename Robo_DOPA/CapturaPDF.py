from selenium import webdriver
from selenium.webdriver.common.by import By
import time

navegador=webdriver.Chrome()

navegador.get("https://www2.portoalegre.rs.gov.br/dopa/")
navegador.find_element(by=By.XPATH, value='//*[@id="coluna_2"]/table/tbody/tr[2]/td[1]/a[2]').click()
time.sleep(20)

