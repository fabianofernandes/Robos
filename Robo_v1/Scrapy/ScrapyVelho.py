#Esse script realiza a busca na web (página DOE) e download dos Editais.
#Abaixo estão sendo executados os passos mapeados:
#1.Acessar a página - https://doe.sea.sc.gov.br/index.php/buscar-jornal/
#2.Buscar um ou mais editais;
#3.Identificar no edital se o número de aprovação do GGG está no edital;
#4.Incluir o(s) links do(s) edital(is) em uma planilha para importar para o banco;
#Ao final do script é gerado um arquivo no formato csv - listaEditais.csv

#Bibliotecas usadas
from bs4 import BeautifulSoup
import urllib.request as urllib_request
import pandas as pd
import requests
import unicodedata
import re
import time
from os.path import basename, join
from urllib.request import Request, urlopen
import win32com.client as win32

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

# Programa Principal
# Captura todos os Editais em todas as Paginas
numeroPag = 0
url = 'https://portal.doe.sea.sc.gov.br/#/buscar-edicao'

response = urlopen(url)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')
paginacao = soup.find('ul', { "class": "pagination wpdm-pagination pagination-centered text-center"})
editais = []

while paginacao.find('a', { 'class': 'next page-numbers'}):
    numeroPag = numeroPag+1
    url = 'https://doe.sea.sc.gov.br/index.php/buscar-jornal/?cp=' + str(numeroPag)
    response = urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    paginacao = soup.find('ul', { "class": "pagination wpdm-pagination pagination-centered text-center"})
    dadosEdital = []
    for edital in soup.find_all("div", {"class": "col-lg-12 col-md-12 col-sm-12"}):
        dadosEdital = []
        aEdital = edital.find('a')
        nomeEdital = aEdital.get_text()
        enderecoEdital = aEdital['href']
        divLinkdownload = edital.find('div', {"class": "ml-3 wpdmdl-btn"})
        aLinkdownload = divLinkdownload.find('a')
        hrefLinkdownload = aLinkdownload['data-downloadurl']
        #print(nomeEdital," ",enderecoEdital, " ", hrefLinkdownload)
        dadosEdital.append(nomeEdital)
        dadosEdital.append(enderecoEdital)
        dadosEdital.append(hrefLinkdownload)
        editais.append(dadosEdital)
    #print(numeroPag)
print (editais)
#construção do data frame
df = pd.DataFrame (editais, columns = ['nomeEdital', 'urlEdital','linkDownloadEdital'])
#imprime as cinco primeira linhas do DF
print (df)
df.to_csv("C:/Robo/listaEditais.csv", sep=';', encoding='utf-8')
caminho = 'C:/Robo/Scrapy/Fonte/'
df = pd.read_csv("C:/Robo/listaEditais.csv", sep=";")

for row in df.itertuples():
    nomeArquivo = (removerAcentosECaracteresEspeciais(str(row.nomeEdital))+'.pdf')
    response = requests.get(str(row.linkDownloadEdital))   
    with open(caminho+nomeArquivo, 'wb') as f:
        f.write(response.content)
        print("Gravado")
    time.sleep(1)