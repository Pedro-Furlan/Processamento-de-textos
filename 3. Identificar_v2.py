import re
import os
from tkinter import Tk
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from isbnlib import meta
from isbnlib import doi2tex

Tk().withdraw()

global diretorio_trabalho
diretorio_trabalho = filedialog.askdirectory(title = "Escolha o diretório de trabalho")

def CarregarTextos(): # Gera dicionário no formato {caminho do arquivo: [nome do arquivo, conteudo do arquivo]}

    global caminhos_arquivos
    caminhos_arquivos = list(askopenfilename(filetypes = [('Arquivos de texto', '*.txt')], title = "Escolha o(s) arquivo(s) de texto a serem processados", multiple = True))

    textos = {}

    for caminho in caminhos_arquivos:
        arquivo = open(caminho, "r", encoding = "utf-8")
        conteudo = arquivo.read()
        arquivo.close()
        nome = os.path.basename(caminho)

        lista_aux = []
        lista_aux.append(nome)
        lista_aux.append(conteudo)
        textos[caminho] = lista_aux

    return textos


def ChecarCodigos(textos):

    # Listagem dos tipos e códigos (ISBN ou DOI)
    dicts_tipo_codigo = {}

    for i in range(len(textos)):

        conteudo2 = textos[caminhos_arquivos[i]][1]
        nome2 = textos[caminhos_arquivos[i]][0]

        # Identificando a presença de ISBN ou do DOI
        isbn_doi = str(re.findall(r'ISBN|DOI', conteudo2))
        isbn_doi = isbn_doi[2:-2]

        # Adicionando códigos às listas de códigos ISBN ou DOI
        if isbn_doi == 'ISBN':
            isbn = str(re.findall(r'(?<=ISBN:)\s+(\d+\-\d+\-\d+\-\d+\-\d)', conteudo2))
            dicts_tipo_codigo[nome2] = [isbn_doi, isbn[2:-2]]

        elif isbn_doi == 'DOI':
            doi = str(re.findall(r'(?<=DOI:)\s+(.+)', conteudo2))
            dicts_tipo_codigo[nome2] = [isbn_doi, doi[2:-2]]

    return dicts_tipo_codigo



def BuscarMetadados(codigos):
    
    dicts_principal = {}
    
    for j in range(len(codigos)):

        # Retorna indicação se é DOI ou ISBN
        tipo_cod = codigos[textos[caminhos_arquivos[j]][0]][0]
        
        # Retorna código DOI ou ISBN
        cod = codigos[textos[caminhos_arquivos[j]][0]][1]

        # Trata dados ISBN
        if tipo_cod == 'ISBN':
            
            # Armazena informações do ISBN    
            meta_isbn = str(meta(cod, service='default')) # ESTÁ GERANDO ERRO. Alguns ISBN não estão sendo encontrados.
            
            # Extrai e organiza informações guardadas em meta_isbn
            titulo1 = str(re.findall(r'(?<=\'Title\':)\s+\'(.+)\'+\,+\s+\'Authors\'', meta_isbn))
            titulo1 = titulo1[2:-2]
            autor1 = str(re.findall(r'(?<=\'Authors\':)\s+(.+)\,+\s+\'Publisher\'', meta_isbn))
            autor1 = autor1[2:-2]
            publicacao1 = str(re.findall(r'(?<=\'Publisher\':)\s+\'(.+)\'+\,+\s+\'Year\'', meta_isbn))
            publicacao1 = publicacao1[2:-2]
            ano1 = str(re.findall(r'(?<=\'Year\':)\s+\'(.+)\'+\,+\s+\'Language\'', meta_isbn))
            ano1 = ano1[2:-2]
            ISBN13 = str(re.findall(r'(?<=\'ISBN-13\':)\s+\'(.+)\'+\,+\s+\'Title\'', meta_isbn))
            ISBN13 = ISBN13[3:-3]

            dicts_aux1 = {}

            dicts_aux1['Título'] = titulo1
            dicts_aux1['Autor'] = autor1
            dicts_aux1['Publicação'] = publicacao1
            dicts_aux1['Ano'] = ano1
            dicts_aux1['ISBN-13'] = ISBN13
            
            # Armazena em dicionário os dados organizados
            dicts_principal[caminhos_arquivos[j]] = dicts_aux1

        # Trata dados DOI
        elif tipo_cod == 'DOI':
            
            # Armazena informações do DOI
            meta_doi = doi2tex(cod)

            # Extrai e organiza informações guardadas em meta_doi
            titulo2 = str(re.findall(r'(?<=title =)\s+(\{.+\})', meta_doi))
            autor2 = str(re.findall(r'(?<=author =)\s+(\{.+\})', meta_doi))
            autor2 = autor2[3:-3]
            publicacao2 = str(re.findall(r'(?<=publisher =)\s+(\{.+\})', meta_doi))
            publicacao2 = publicacao2[3:-3]
            ano2 = str(re.findall(r'(?<=year =)\s+(\d\d\d\d)', meta_doi))
            ano2 = ano2[2:-2]
            DOI = str(re.findall(r'(?<=doi =)\s+(\{.+\})', meta_doi))
            DOI = DOI[3:-3]

            dicts_aux2 = {}

            dicts_aux2['Título'] = titulo2
            dicts_aux2['Autor'] = autor2
            dicts_aux2['Publicação'] = publicacao2
            dicts_aux2['Ano'] = ano2
            dicts_aux2['DOI'] = DOI
            
            # Armazena em dicionário os dados organizados
            dicts_principal[caminhos_arquivos[j]] = dicts_aux2
            
            
            # Loop para remover do dicionario os arquivos para os quais não se encontraram dados
            aux = []
            for caminho in dicts_principal:
                for chave in dicts_principal[caminho]:
                    if dicts_principal[caminho][chave] == '':
                        aux.append(caminho)
                        break
            
            for caminho in aux:
                del dicts_principal[caminho]

    return dicts_principal


def Exportar3(dados):
    
    print("O arquivo será gerado no diretorio de trabalho: %s" % os.getcwd())
    arquivo = open("Códigos de identificação e metadados dos arquivos.txt", "a")
    
    for caminho in dados:
        nome_arquivo = os.path.basename(caminho)
        arquivo.write(nome_arquivo + ':\n')
        for chave in dados[caminho]:
            arquivo.write(str(chave) + ': ')
            arquivo.write(str(dados[caminho][chave]) + '\n')
        arquivo.write("\n\n\n")
    arquivo.close()
    
    return None



def Renomear3(dados): # Recebe dicionário no formato {caminho: {nome do metadado: valor do metadado}}
    
    metadados = {'1':'Ano', '2':'Autor', '3':'Publicação', '4':'Título'}
    ordinais = ['primeiro', 'segundo', 'terceiro' ,'quarto']
    ordem_impressao = []
    
    for i in range(4): # Loop que gera a ordem de impressão selecionada pelo usuário
        while True:
            for chave in metadados:
                print("[ %s ] %s\n" % (chave, metadados[chave]))
            aux = input('Digite o numero do %s elemento do título:\n' % ordinais[i])
            if aux not in metadados:
                print("Entrada inválida!\n")
            elif aux in metadados:
                ordem_impressao.append(metadados[aux])
                del metadados[aux]
                break

    
    for caminho in dados:
        diretorio = os.path.dirname(caminho)
        nome = os.path.basename(caminho)
        extensao = os.path.splitext(os.path.basename(caminho))[1]
        
        os.chdir(diretorio)
        
        novo_nome = ""
        flag = 4
        for i in ordem_impressao:
            if i == 'Código':
                if 'DOI' in dados[caminho]:
                    i = 'DOI'
                elif 'ISBN-13' in dados[caminho]:
                    i = 'ISBN-13'
            novo_nome += str(dados[caminho][i])
            if flag > 0:
                novo_nome += ', '
            flag -= 1
        novo_nome += extensao

        try:
            if os.path.isfile(novo_nome):
                print("Já existe um arquivo com o nome")
            else:
                os.rename(nome, novo_nome)
        except OSError:
            continue
            
    os.chdir(diretorio_trabalho)
            
    return None





def Identificar():
    
    global textos
    textos = CarregarTextos()

    textos_temp = textos

    codigos = ChecarCodigos(textos_temp)

    dados = BuscarMetadados(codigos)
    
    while True:
        opt = int(input("Qual operação deseja realizar?\n[ 1 ] Gerar arquivo .txt com os metadados localizados\n[ 2 ] Renomear os arquivos para os quais se identificou metadados\n[ 0 ] Voltar ao menu principal\n\n"))
        
        if opt == 1:
            Exportar3(dados)
    
        elif opt == 2:
            Renomear3(dados)
            
        elif opt == 0:
            break
        
    return None