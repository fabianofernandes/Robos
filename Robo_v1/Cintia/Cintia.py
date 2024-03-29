# Bibliotecas para manipular PDFs
#Esse script realiza a busca nos arquivos pdfs, identificando:
#1.Abrir o arquivo PDF
#2.cria df em branco para carregar o resultado das buscas de GGG e o nome do edital onde se encontra
#3.
#4.
#Ao final do script é gerado um arquivo no formato csv - lista-GGG-Editais_Url.csv
import PyPDF2
from fpdf import FPDF
import base64
import json
import pandas as pd
import unicodedata
import re
import os
import warnings as wa
from bson.py3compat import string_type
# import the Elasticsearch low-level client library
from elasticsearch import Elasticsearch
from os.path import basename, join
import win32
import openpyxl

#############################################################################################
#                                     FUNÇÕES                                               #
############################################################################################

### ignorando warnings do tipo FutureWarning
wa.simplefilter( action='ignore', category= FutureWarning)
pd.options.mode.chained_assignment = None

# Função Remove os carcteres especiais de uma string 'a_string'
def removerAcentosECaracteresEspeciais(a_string):
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', a_string)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    palavraSemAcento = palavraSemAcento.replace(" ", "")
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)

# Função Encontra a posiçao de uma subtring 'sub'em uma String á_str'
def find_all_substring(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        #yield a_str[start:(start+16)] versão 0
        yield a_str[start:(start+13)]
        start += len(sub)

# Função Lê arquivo pdf 'nomearquivo' e retorna um objeto JSON
def convert_pdf_to_json(nomearquivo):
    read_pdf = PyPDF2.PdfFileReader(nomearquivo, strict=False)
    pdf_meta = read_pdf.getDocumentInfo()
    num = read_pdf.getNumPages()
    print ("PDF pages:", num)
    all_pages = {}
    all_pages["meta"] = {}
    for meta, value in pdf_meta.items():
        print (meta, value)
        all_pages["meta"][meta] = value
    for page in range(num):
        data = read_pdf.getPage(page)
        #page_mode = read_pdf.getPageMode()
        page_text = data.extractText()
        all_pages[page] = page_text
    json_data = json.dumps(all_pages)
    return json_data


#############################################################################################
#                                PROGRAMA PRINCIPAL                                         #
#############################################################################################

#Programa Principal
if __name__ == '__main__':
    
    #Define o nome do arquivo csv fonte com a lista de arquivos baixados lê e converte em DF
    #lista_arquivos_baixados = "listaEditais.csv" 
    #caminhoProjeto = os.path.dirname(__file__) 
    #caminho = os.path.join(caminhoProjeto, 'fonte\\')
    os.chdir('C:\\Robo')
    arquivo_saida = "C:\\Robo\\AS_SO.csv"
    arquivo_entrada = 'C:\\Robo\\listaEditais.csv'
    caminho = 'C:\\Robo\\Scrapy\\Fonte\\'
    print (arquivo_entrada)
    df = pd.read_csv(arquivo_entrada, sep=";")
    
    #cria df em branco para carregar o resultado das buscas de GGG e o nome do edital onde se encontra
    column_names = ['AS_SO','edital', 'url_Edital' ]
    #dataframe em branco
    df_out = pd.DataFrame(columns=column_names)
    
    for row in df.itertuples():
        #cria o nome do arquivo
        file = removerAcentosECaracteresEspeciais(str(row.nomeEdital))+'.pdf'
        url_Edital=str(row.urlEdital)
        # Converte o arquivo PDF em JSON
        json_file = convert_pdf_to_json(caminho+file)
        json_file.encode("utf-8")
        # Converte o JSON em String e faz os tratamento para pegar a Sequencia de caracteres depois do GGG
        json_file_string = string_type(json_file)
        json_file_string = json_file_string.replace(":","")
        json_file_string = json_file_string.replace("\\n","")
        json_file_string = json_file_string.rstrip()

        #Procura a sequência de caracteres no json_file_string retorna uma lista com todos 
        list_GGG = list(find_all_substring(json_file_string,"2022SO")) 
        # Converte em Dataframe e junta com o DF principal    
        df_append_out = pd.DataFrame({'AS_SO':list_GGG})
        df_append_out['edital']= file
        df_append_out['url_Edital']= url_Edital
        df_out = df_out.append(df_append_out)

        list_GGG = list(find_all_substring(json_file_string,"2022AS")) 
        # Converte em Dataframe e junta com o DF principal    
        df_append_out = pd.DataFrame({'AS_SO':list_GGG})
        df_append_out['edital']= file
        df_append_out['url_Edital']= url_Edital
        df_out = df_out.append(df_append_out)

        list_GGG = list(find_all_substring(json_file_string,"2021SO")) 
        # Converte em Dataframe e junta com o DF principal    
        df_append_out = pd.DataFrame({'AS_SO':list_GGG})
        df_append_out['edital']= file
        df_append_out['url_Edital']= url_Edital
        df_out = df_out.append(df_append_out)

        list_GGG = list(find_all_substring(json_file_string,"2021AS")) 
        
        # Converte em Dataframe e junta com o DF principal    
        df_append_out = pd.DataFrame({'AS_SO':list_GGG})
        df_append_out['edital']= file
        df_append_out['url_Edital']= url_Edital
        df_out = df_out.append(df_append_out)
       
        
    # salva o df com o resultado em um arquivo CSV
    df_out.to_csv(arquivo_saida, sep=';', encoding='utf-8')

