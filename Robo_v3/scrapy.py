
#Esse script realiza a busca na web (página DOE) e download dos Editais.
#Abaixo estão sendo executados os passos mapeados:
#1.Acessar a página - https://doe.sea.sc.gov.br/index.php/buscar-jornal/
#2.Buscar um ou mais editais;
#3.Identificar no edital se o número de aprovação do GGG está no edital;
#4.Incluir o(s) links do(s) edital(is) em uma planilha para importar para o banco;
#Ao final do script é gerado um arquivo no formato csv - listaEditais.csv

#Bibliotecas usadas
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service

from os import path
import sys

import glob
import shutil
import os
from bs4 import BeautifulSoup
import urllib.request as urllib_request
import pandas as pd
import requests
import unicodedata
import re
import time
from os.path import basename, join
from urllib.request import Request, urlopen

def conectarBrowserFirefox(download_dir):
    #options = Options()
    options = webdriver.FirefoxOptions()
    caminho_Gecko='c:\\Python\\geckodriver.exe'
    servico_gecko = Service(executable_path=caminho_Gecko)
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.folderList", 2)
    #options.set_preference("browser.download.manager.useWindow", False)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                        "application/pdf, application/force-download")
    # opcoes para o navegadro nao abrir 
    #options.add_argument("--headless")
    #options.add_argument('--disable-gpu')
    options.binary_location = r"C:\\Program Files (x86)\\Mozilla Firefox2\\firefox.exe"
    driverFirefox = webdriver.Firefox(service=servico_gecko, options=options)
    return driverFirefox

#função para remover acentos e caracteres especiais
def removerAcentosECaracteresEspeciais(palavra):
    # Unicode normalize transforma um caracter em seu equivalente em latin. formas de normalização
    #normalizar é o ato de transformar strings (textos no padrão unicode), Isso facilita a comparação, 
    # indexação e ordenação de strings já que, em um sistema “normalizado”, essas operações são é mais confiáveis.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    palavraSemAcento = palavraSemAcento.replace(" ", "")
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)

def aguardaArquivoCarregar(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 20:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.part'):
                dl_wait = True
        seconds += 1
    return seconds

    
    
                    
#############################################################################################
#                                PROGRAMA PRINCIPAL                                         #
#############################################################################################

if __name__ == '__main__':
    # Captura todos os Editais em todas as Paginas
   
    caminho_download = "C:\\Novo_Robo\\fonte"
    fonte_dir = "C:\\Novo_Robo\\fonte\\"
    caminhoDestinoPDF = "C:\\Novo_Robo\\servidor\\"
    arquivo_saida = "M:\\CIES\\000 - Carga_Robo\\Arquivo_Entrada\\listaEditaisv3.csv "
    
    
    #arquivo_saida = "C:\\Novo_Robo\\listaEditaisv3.csv "

    #cria df em branco para carregar o resultado das buscas de GGG e o nome do edital onde se encontra
    column_names = ['nomeEdital','urlEdital']
    df_out = pd.DataFrame(columns=column_names)
    
    #configura e cria o navegador para usar o biblioteca selenium
    driver = conectarBrowserFirefox(caminho_download)

    os.chdir (caminho_download)
    
    # Pagina Inicial
    #Verificar a versão da página, pois em cada atualização mudam a vXXX
    driver.get("https://portal.doe.sea.sc.gov.br/v127/#/buscar-edicao")
    #+driver.get("https://portal.doe.sea.sc.gov.br/v125/#/buscar-edicao")
    
    
    
    try:
        paginaInicial = WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.XPATH, "/html/body/app-root/app-home-jornal/div/app-jornal/div/div/div/div[2]/p-dataview/div/div[1]/div/div/p-dataviewlayoutoptions/div/button[2]")))
    except:
        print("----- pagina inicial nao carregou---------")
    time.sleep(5)
    numeroPag = 0
    #criar o dataframe (importar o codigo dos outros)
    while True:
        if numeroPag == 0:
            numeroPag = numeroPag + 1
        else:
            #linha inserida no dia 17/03/2023 - resultado foi o mesmo         
            #driver.find_element(By.XPATH, '//*[@id="checkbox"]').click()
            driver.find_element(By.XPATH,'//span[@class="p-paginator-icon pi pi-angle-right"]').click()
            #driver.find_element_by_xpath("/html/body/app-root/app-home-jornal/div/app-jornal/div/div/div/div[2]/p-dataview/div/p-paginator/div/button[3]").click()
            #driver.find_element(By.XPATH,"/html/body/app-root/app-home-jornal/div/app-jornal/div/div/div/div[2]/p-dataview/div/p-paginator/div/button[3]").click()
            time.sleep(5)
        # para testar insere break 
        if numeroPag == 10:
            break
        numeroPag = numeroPag + 1
        # Inserir o looping para realizar todos os downloads
        while True:
            try:
                #elements = driver.find_elements(By.XPATH, '//button[@class="p-ripple p-element p-button p-component"]')
                time.sleep(4)
                nomesEditais = driver.find_elements(By.XPATH, '//span[@class="font-bold"]')
                #listaNomeData = driver.find_elements(By.XPATH, '//button[@class="p-ripple p-element p-button p-component"]') 
                time.sleep(4)
                #print(nomesEditais       "p-element p-ripple p-button-outlined p-button p-component
                # Aqui esta o erro 
                #button_xpath = '//button[starts-with(@class, "p-element p-ripple p-button-outlined") and ends-with(@class, "p-button p-component")]'
                #buttons = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//button[starts-with(@class, "p-element p-ripple p-button-outlined") and ends-with(@class, "p-button p-component")]')))
                #buttons = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//button[starts-with(@class, "p-element p-ripple p-button-outlined") and substring(@class, string-length(@class) - string-length("p-button p-component") + 1) = "p-button p-component"]')))
                buttons = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="p-button-label" and contains(text(), "Download")]')))
                for button,nomeEdital in zip((buttons[::2]),range(0, len(nomesEditais), 2)):    
                    time.sleep(4)
                    # aqui precisa alterar a logica para buscar no link do Fabiano
                    driver.implicitly_wait(5)
                    driver.execute_script("arguments[0].click();", button)
                    #button.click()
                    aguardaArquivoCarregar(fonte_dir)
                    nome = nomesEditais[nomeEdital].text
                    nome = removerAcentosECaracteresEspeciais(nome[8:])
                    print(nome)
                    arquivoBaixado = (glob.glob("*.pdf"))
                    shutil.move (fonte_dir+arquivoBaixado[0],caminhoDestinoPDF+ nome+'.pdf')
                    #salvar no csv o nome do arquivo
                    url = caminhoDestinoPDF + removerAcentosECaracteresEspeciais(nome)+'.pdf'
                    df_out = df_out.append({'nomeEdital': nome, 'urlEdital':url}, ignore_index=True)
                    print("---carregou---", button, " ", nome, " ", arquivoBaixado[0] )
                    time.sleep(2)
                    # para excluir os arquivos de uma pasta
                    #for f in arquivoBaixado:
                    #    try: 
                    #        os.remove(fonte_dir+f)
                    #    except OSError as e:
                    #        print("Error: %s : %s" % (f, e.strerror))
            except TimeoutException:
                print("Tempo limite excedido ao esperar pelo elemento clicável.")
            except ElementClickInterceptedException:
                print("Outro elemento está interceptando o elemento que deve ser clicado.")
            except WebDriverException as e:
                print (e)
                print("-----ERRO NA PAGINA ",numeroPag," ---------")
                break
            break
        print("-----terminou a PAGINA ",numeroPag," ---------")
    
    df_out.reset_index(inplace=True, drop=True)
    df_out.to_csv(arquivo_saida, sep=';', encoding='utf-8')
driver.quit()
