#--------------------------------------------------------------------------------------
# Preâmbulo: Importando e carregando pacotes; definindo diretório de trabalho
#--------------------------------------------------------------------------------------

import nltk # Funções de processamento de linguagem natural
import os # Funções de manipulação de arquivos e diretórios do sistema operacionao
import shutil
import math
import re
import sys
from time import sleep
from isbnlib import meta
from isbnlib import desc
from isbnlib import doi2tex
from isbnlib.registry import bibformatters
from tkinter import Tk # tkinter é um módulo para interfaces gráficas
from tkinter import filedialog    
from tkinter.filedialog import askopenfilename # Importando função para interface gráfica de seleção de arquivos
from nltk.stem.snowball import SnowballStemmer # Importando o módulo de stemming (extração de radicais das palavras)
from nltk.tokenize import RegexpTokenizer # Módulo a ser utilizado para remover pontuação

nltk.download('stopwords', quiet = True)
nltk.download('wordnet', quiet = True)
nltk.download('punkt', quiet = True)

derivador = SnowballStemmer('english') # Também disponível em outros idiomas

Tk().withdraw() # Evita que apareça uma janela indesejada








#--------------------------------------------------------------------------------------
# 0. Selecionando os textos de trabalho
#--------------------------------------------------------------------------------------

def CarregarTextos(): # Gera dicionário no formato {caminho do arquivo: [nome do arquivo, conteudo do arquivo]}
    
    global caminhos_arquivos
    caminhos_arquivos = list(askopenfilename(initialdir= os.getcwd(), # Selecionando arquivo(s) de texto.
                           filetypes = [('Arquivos de texto', '*.txt')],
                           title = "Escolha o(s) arquivo(s) de texto a serem processados",
                           multiple = True))  
    global textos
    textos = {}
    
    for caminho in caminhos_arquivos: 
        arquivo = open(caminho, "r", encoding = "utf-8")
        conteudo = arquivo.read().lower()
        arquivo.close()
        nome = os.path.basename(caminho)
        
        lista_aux = []
        lista_aux.append(nome)
        lista_aux.append(conteudo)
        textos[caminho] = lista_aux
      
    return textos








#-----------------------------------------------------------------------------
# 1. Menu de opções
#-----------------------------------------------------------------------------

def Menu(textos):

    while True:
        
        opcao = input('\nDigite o número  da função desejada:\n[ 1 ] Sumário do conteúdo\n[ 2 ] Identificação de códigos DOI e ISBN\n[ 3 ] Classificação do texto\n[ 4 ] Seleção de arquivos\n[ 0 ] Sair\n\n')
    
    
        if opcao == '0':
            opt = input("\nO programa será encerrado. Digite 'q' para continuar.\n")
            if opt.lower() == 'q':
                break
            
        elif opcao == '1':
            print("\nOpção escolhida: Sumário\n")
            Sumarizar()
        
        elif opcao == '2':
            print("\nOpção escolhida: Identificação\n")
            Identificar(textos)
        
        elif opcao == '3':
            print("\nOpção escolhida: Classificação\n")
            Classificar()
        
        elif opcao == '4':
            print("\nOpção escolhida: Seleção de arquivos. A nova seleção irá substituir a anterior!\n")
            CarregarTextos()
        
        elif opcao != '1' or '2' or '3' or '4' or '0':
            opcao = int(input("\nEntrada inválida.\n"))








#--------------------------------------------------------------------------------------
# 2. Função de sumarização de textos
#--------------------------------------------------------------------------------------
    
def TokenizarTextos2(textos_temp): # Retorna dicionário no formato {caminho do arquivo: [nome do arquivo, [lista de tokens]]}
  
    textos_token = {}
    tokenizer = RegexpTokenizer(r'\w+')
    
    for caminho in textos_temp:
        conteudo = textos_temp[caminho][1]
        lista_tokenizada = tokenizer.tokenize(conteudo)
        # lista_tokenizada = nltk.tokenize.word_tokenize(conteudo) # Tokenizador retorna uma lista
        
        lista_aux = []
        lista_aux.append(textos_temp[caminho][0])
        lista_aux.append(lista_tokenizada)
        
        textos_token[caminho] = lista_aux
    
    return textos_token 




def RemoverStopwords2(textos_temp): # Mantém o formato dicionario {caminho do arquivo: [nome do arquivo, [lista de tokens sem stopwords]]}
    
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords += str(range(0,10))
        
    for caminho in textos_temp:
        lista_tokens = textos_temp[caminho][1]
        lista_tokens = [token for token in lista_tokens if token.lower() not in stopwords] # Remove as stopwords
        
        del textos_temp[caminho][1]
        textos_temp[caminho].append(lista_tokens)

    return textos_temp





def RaizGramatical2(textos_temp): # Mantém o formato dicionario {caminho do arquivo: [nome do arquivo, [lista de tokens em forma radical]]} 
      
    for caminho in textos_temp:
        
        conteudo = textos_temp[caminho][1]
        
        lista_raizes = [derivador.stem(token) for token in conteudo] # Derivador itera sobre uma lista, e retorna outra lista
        del textos_temp[caminho][1]
        textos_temp[caminho].append(lista_raizes)
        
    return textos_temp





def RemontarTextos2(textos_temp): # Retorna dicionario no formato {caminho do arquivo: [nome do arquivo, texto]}
    
    textos_remontado = {}
    
    for caminho in textos_temp:
        string = ""
        for j in textos_temp[caminho][1]:
            string += j
            string += " "
        lista_aux = []
        lista_aux.append(textos_temp[caminho][0])
        lista_aux.append(string)
        textos_remontado[caminho] = lista_aux
        
    return textos_remontado





def PontuarPalavras(textos_temp, texto_remontado): # Recebe dicionário {caminho do arquivo: [nome do arquivo, [lista de tokens]]} e retorna dicionario aninhado {caminho: {palavra: nº de ocorrencias}}
    
    ocorrencias = {}
    
    for caminho in textos_temp:
        ocorrencias_por_palavra = {}
        for palavra in textos_temp[caminho][1]:
            ocorrencias_por_palavra[palavra] = texto_remontado[caminho][1].count(palavra)
        ocorrencias[caminho] = ocorrencias_por_palavra
    
    return ocorrencias
    




def TokenizarFrases(textos_temp2): # Recebe dicionario {caminho do arquivo: [nome do arquivo, conteudo]}
    
    frases= {}
    
    for caminho in textos_temp2:
        conteudo = textos_temp2[caminho][1]
        lista_tokenizada = nltk.tokenize.sent_tokenize(conteudo) # Tokenizador retorna uma lista
        
        lista_aux = []
        lista_aux.append(textos_temp2[caminho][0])
        lista_aux.append(lista_tokenizada)
        
        frases[caminho] = lista_aux
    
    return frases 
        
        



def PontuarFrases(frases, pontuacao_por_palavra): # Recebe dois dicionarios, um no formato {caminho: [nome do arquivo, [ĺista de frases]]}, e outro no formato {caminho: {palavra: pontuação}}; e retorna outro dicionario no formato {caminho: [nome do arquivo, [[frase, pontuação]]]}
    
    pontuacao_por_frase = {}
    
    for caminho in frases:
        lista_frases = frases[caminho][1]
        lista_pares = []
        for frase in lista_frases:
            lista_frase_pont = []
            pontuacao_da_frase = 0
            for palavra in pontuacao_por_palavra[caminho]:
                ocorrencias = frase.count(palavra)
                pontos = ocorrencias * pontuacao_por_palavra[caminho][palavra]
                pontuacao_da_frase += pontos
            lista_frase_pont.append(frase)
            lista_frase_pont.append(pontuacao_da_frase)
            lista_pares.append(lista_frase_pont)
        lista_nome_lista = []
        lista_nome_lista.append(os.path.basename(caminho))
        lista_nome_lista.append(lista_pares)
        pontuacao_por_frase[caminho] = lista_nome_lista
            
    
    return pontuacao_por_frase
    



def ExtrairFrases(pontuacao_por_frase, fator_compressao): # Recebe dicionario no formato {caminho: [nome do arquivo, [[frase, pontuação]]]}, e retorna dicionario no formato {caminho: [nome do arquivo, texto resumido]}
    
    textos_resumidos = {}
    
    for caminho in pontuacao_por_frase:
        
        lista_de_pares = pontuacao_por_frase[caminho][1]
        
        num_frases_antes = len(lista_de_pares)
        num_frases_depois = int(math.ceil(((fator_compressao/100) * num_frases_antes)))
        eliminar = num_frases_antes - num_frases_depois
        
        lista_pontuacoes = []
        for i in lista_de_pares:
            lista_pontuacoes.append(i[1])
        lista_pontuacoes.sort()
        del lista_pontuacoes[:eliminar]
        valor_min = lista_pontuacoes[0]
        
        for par in lista_de_pares:
            if par[1] <= valor_min:
                lista_de_pares.remove(par)
        
        texto_reconstruido = ""
        for par in lista_de_pares:
            texto_reconstruido += par[0]
            texto_reconstruido += " "
        
        lista_nome_texto = []
        lista_nome_texto.append(os.path.basename(caminho))
        lista_nome_texto.append(texto_reconstruido)
        
        textos_resumidos[caminho] = lista_nome_texto
    
    return textos_resumidos





def Exportar2(textos_resumidos):
      
    opc = input("Opções de exportação:\n[ 1 ] Gerar um arquivo para cada texto resumido\n[ 2 ] Gerar um único arquivo com todos os resumos\n")
    
    if opc == '1':
    
        print("Os arquivos serão gerados no diretorio de trabalho: %s" % os.getcwd())
              
        for caminho in textos_resumidos:
            arquivo = open(textos_resumidos[caminho][0],"a")
            arquivo.write("%s:\n\n%s" % (textos_resumidos[caminho][0],textos_resumidos[caminho][1]))
            arquivo.close
         
            
    elif opc == '2':
        
        print("O arquivo será gerado no diretorio de trabalho: %s" % os.getcwd())
    
        arquivo = open("Textos resumidos.txt", "a")
        
        for caminho in textos_resumidos:
            arquivo.write("%s:\n\n%s\n\n\n\n\n" % (textos_resumidos[caminho][0],textos_resumidos[caminho][1]))
      
        arquivo.close() 
             
        
    return None




def Exibir2(textos_resumidos):
    
    for caminho in textos_resumidos:
        
        opc = input("Opções de exibição:\nPressione 'Enter' para exibir o próximo texto resumido\nDigite 1 para exibir todos os textos em sequência\nDigite 0 para sair\n")
        
        print("\n%s:\n\n%s\n\n" % (textos_resumidos[caminho][0],textos_resumidos[caminho][1]))
        
        if opc == '1':
            for caminho in textos_resumidos:
                print("%s:\n\n%s\n\n\n\n\n" % (textos_resumidos[caminho][0],textos_resumidos[caminho][1]))
            break
        
        if opc == '0':
            break
        
    return None
    




def Sumarizar():
     
    textos_temp = textos # Variável temporária evita alterar a variável principal, que será novamente utilizada posteriormente
    
    textos_temp = TokenizarTextos2(textos_temp) # Divide o texto em palavras
    
    textos_temp = RemoverStopwords2(textos_temp) # Remove palavras que carregam pouca informação, como artigos e pronomes
    
    textos_temp = RaizGramatical2(textos_temp) # Deixa as palavras na forma radical
    
    texto_remontado = RemontarTextos2(textos_temp) # Necessário ser um dicionario separado, pois se contará a ocorrência de palavras no texto como um todo
    
    pontuacao_por_palavra = PontuarPalavras(textos_temp, texto_remontado)

    textos_temp2 = textos # Variável que será separada em frases
    
    frases = TokenizarFrases(textos_temp2)
       
    pontuacao_por_frase = PontuarFrases(frases, pontuacao_por_palavra)
    
    
    while True:
    
        fator_compressao = float(input("Digite um numero de 1 a 100 correspondente ao percentual de compressão a ser aplicado nos textos - isto é, quantos % das frases do texto original devem ser mantidas:\n"))
        
        if fator_compressao > 1.0 and fator_compressao < 100.0:
            break
        
        else:
            continue
        
        
    textos_resumidos = ExtrairFrases(pontuacao_por_frase, fator_compressao)
    
    
    while True:
        opt = input("Qual operação deseja realizar agora?\n[ 1 ] Exibir os resumos na tela\n[ 2 ] Gerar arquivos de texto com os resumos\n[ 0 ] Voltar ao menu principal\n\n")
        
        if opt == '1':
            Exibir2(textos_resumidos)
            
        elif opt == '2':
            Exportar2(textos_resumidos)
            
        elif opt == '0':
            break
        
    return None








#--------------------------------------------------------------------------------------
# 3. Função de identificação de códigos DOI e ISBN
#--------------------------------------------------------------------------------------


def ChecarCodigos(textos):

    # Listagem dos tipos e códigos (ISBN ou DOI)
    global dicts_tipo_codigo
    dicts_tipo_codigo = {}
    
    for i in range(1):

        conteudo = textos[caminhos_arquivos[i]][1]
        nome = textos[caminhos_arquivos[i]][0]

        # Identificando a presença de ISBN ou do DOI
        isbn_doi = str(re.findall(r'ISBN|DOI', conteudo))
        isbn_doi = isbn_doi[2:-2]

        # Adicionando códigos às listas de códigos ISBN ou DOI
        if isbn_doi == 'ISBN':
            isbn = str(re.findall(r'(?<=ISBN:)\s+(\d+\-\d+\-\d+\-\d+\-\d)', conteudo))
            dicts_tipo_codigo[nome] = [isbn_doi, isbn[2:-2]]

        elif isbn_doi == 'DOI':
            doi = str(re.findall(r'(?<=DOI:)\s+(.+)', conteudo))
            dicts_tipo_codigo[nome] = [isbn_doi, doi[2:-2]]

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
    
    print("O arquivo será gerado no diretorio de trabalho: %s\n" % os.getcwd())
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





def Identificar(textos):
      
    codigos = ChecarCodigos(textos)
    
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








#--------------------------------------------------------------------------------------
# 4. Função de classificação de textos
#--------------------------------------------------------------------------------------

def ReordenarNGramas(raizes): # Reagrupa n-gramas de tamanho até 3
    
    aux = []
    aux2 = None
    i = 0
    while i < len(raizes):
        if raizes[i] != ';' and raizes[i + 1] == ';':
            aux.append(raizes[i])
            i += 2
        elif raizes[i] != ';' and raizes[i + 1] != ';' and raizes[i + 2] == ';':
            aux2 = raizes[i] + " " + raizes[i + 1]
            aux.append(aux2)
            i += 3
        elif raizes[i] != ';' and raizes[i + 1] != ';' and raizes[i + 2] != ';' and raizes[i + 3] == ';':
            aux2 = raizes[i] + " " + raizes[i + 1] + " " + raizes[i + 2]
            aux.append(aux2)
            i += 4
    
    return aux


def ReceberRaizes(caminho): # Recebe um caminho de arquivo e retorna uma lista com as palavras daquele arquivo
        
    arquivo = open(caminho, "r", encoding = "utf-8") # Abrindo arquivo
    conteudo = arquivo.read() # Extraindo conteudo
    arquivo.close()
    
    conteudo = conteudo.lower() # Deixando todas as letras minúsculas
    
    if conteudo[len(conteudo)-1] != "\n":
        conteudo = conteudo + "\n"
    conteudo = conteudo.replace("\n", ";\n") # Colocando ';' no fim os itens para evitar erro
    conteudo = conteudo[:-1]
    
    tokens = nltk.tokenize.word_tokenize(conteudo) # Separação em tokens individuais
        
    raizes = [derivador.stem(token) for token in tokens] # Aplicando o stemming
     
    raizes = ReordenarNGramas(raizes) # Reagrupa n-gramas
    raizes = set(raizes) # Transforma em set para eliminar elementos repetidos
    raizes = list(raizes) # Transforma de volta em lista
    raizes = sorted(raizes) # Por fim, ajeita em ordem alfabética por facilidade
        
    return raizes # Retorna lista de palavras pertencentes a uma categoria


def ImportarVocabulario(): # Não recebe parâmetros, pois abrirá janela para usuário selecionar arquivos onde está o vocabulário (precisam todos estar na mesma pasta), e retorna um objeto dicionario no formato {nome da cateogoria: [lista de palavras]}

    caminhos_arquivos = list(askopenfilename(initialdir= os.getcwd(), # Selecionando arquivo(s) de vocab.
                           filetypes = [('Arquivos de texto', '*.txt')],
                           title = "Escolha o(s) arquivo(s) de texto com os vocabulários",
                           multiple = True))    
        
    vocab = {} 
             
    for caminho in caminhos_arquivos:
        categoria = os.path.basename(caminho) # Extraindo os nomes dos arquivos de seus caminhos (c/ extensão)
        categoria = os.path.splitext(categoria) # Dando às categorias o nome sem a extensão
        vocab[categoria[0]] = ReceberRaizes(caminho)
    
    return vocab





def TokenizarTextos4(textos_temp): # Retorna dicionário no formato {caminho do arquivo: [nome do arquivo, [lista de tokens]]}

    textos_token = {}
    tokenizer = RegexpTokenizer(r'\w+')
    
    for caminho in textos_temp:
        conteudo = textos_temp[caminho][1]
        lista_tokenizada = tokenizer.tokenize(conteudo)
        
        
        lista_aux = []
        lista_aux.append(textos_temp[caminho][0])
        lista_aux.append(lista_tokenizada)
        
        textos_token[caminho] = lista_aux
    
    return textos_token 





def RemoverStopwords4(textos_temp): # Mantém o formato dicionario {caminho do arquivo: [nome do arquivo, [lista de tokens sem stopwords]]}
    
    stopwords = nltk.corpus.stopwords.words('english')
        
    for caminho in textos_temp:
        lista_tokens = textos_temp[caminho][1]
        lista_tokens = [token for token in lista_tokens if token.lower() not in stopwords] # Remove as stopwords
        
        del textos_temp[caminho][1]
        textos_temp[caminho].append(lista_tokens)

    return None





def RaizGramatical4(textos_temp): # Mantém o formato dicionario {caminho do arquivo: [nome do arquivo, [lista de tokens em forma radical]]} 
      
    for caminho in textos_temp:
        
        conteudo = textos_temp[caminho][1]
        
        lista_raizes = [derivador.stem(token) for token in conteudo] # Derivador itera sobre uma lista, e retorna outra lista
        del textos_temp[caminho][1]
        textos_temp[caminho].append(lista_raizes)
        
    return None





def RemontarTextos4(textos_temp): # Retorna dicionario no formato {caminho do arquivo: [nome do arquivo, conteudo do arquivo preparado para classificação]}
       
    for caminho in textos_temp:
        string = ""
        #for j in range(0, len(textos_temp[i][1])):
        for j in textos_temp[caminho][1]:
            string += j
            string += " "
        textos_temp[caminho][1] = string
        
    return None





def Classify(textos_temp, vocabulario): # Recebe dicionário com os textos_temp {caminho do arquivo: [nome do arquivo, texto preparado para processamento]}, e outro com os vocabulários {categoria: [lista de palavras da categoria]}. Retorna dicionário {caminho do arquivo: [nome do arquivo, categoria do arquivo]}
    
    classificacao = {}

    for caminho in textos_temp: 
        ocorrencias_por_categoria = {}
        for categoria in vocabulario:
            ocorrencias = 0
            for palavra in vocabulario[categoria]: 
                ocorrencias += textos_temp[caminho][1].count(palavra)
            ocorrencias_por_categoria[categoria] = ocorrencias
        
        # print(ocorrencias_por_categoria)
        categoria_max = max(ocorrencias_por_categoria, key = ocorrencias_por_categoria.get) # Procurando categoria com maior numero de ocorrencias
        # print(categoria_max)
        
        lista_aux = []
        lista_aux.append(textos_temp[caminho][0])
        lista_aux.append(categoria_max)
        classificacao[caminho] = lista_aux
    
    return classificacao 





def Exportar4(classificacao):
    
    print("O arquivo será gerado no diretorio de trabalho: %s" % os.getcwd())
    arquivo = open("Classificação dos arquivos.txt", "a")
    for caminho in classificacao:
        arquivo.write("%s : %s\n" % (classificacao[caminho][0], classificacao[caminho][1]))
    arquivo.close()
    
    return None





def Mover(classificacao, vocabulario):

    for categoria in vocabulario: # Loop que verifica a existência das pastas e, caso não existam, as cria 
        if not os.path.exists(categoria):
            os.mkdir(categoria)

    for caminho in classificacao: # Move o arquivo com base no caminho completo para a pasta com nome (caminho relativo)
        shutil.move(caminho, classificacao[caminho][1])

    return None





def Classificar():
    
    textos_temp = textos # Variável criada para evitar alterações na variável principal, o que impediria o funcionamento das demais funções
    
    mensagem = "\nEscolha os arquivos de texto que contém o vocabulário a ser usado na classificação. No máximo 3 palavras por linha!"
    for letra in mensagem:
        sleep(0.015) # In seconds
        sys.stdout.write(letra)
        sys.stdout.flush()
    sleep(2)
    
    vocabulario = ImportarVocabulario() # Usuário seleciona arquivos de texto. O título desses arquivos deve ser o nome da categoria, e seu conteúdo deve ser uma lista de até 3 palavras por vez (por exemplo, "ciência da computação") que será utilizadas na classificação
    
    textos_temp = TokenizarTextos4(textos_temp) # Divide o texto em palavras individuais
    
    RemoverStopwords4(textos_temp) # Remove palavras que carregam pouca informação, como artigos e pronomes
    
    RaizGramatical4(textos_temp) # Deixa as palavras na sua forma radical, sem sufixos
    
    RemontarTextos4(textos_temp) # Remonta o texto para análise classificatória
    
    classificacao = Classify(textos_temp, vocabulario) # Função principal da classificação. 
    
    while True:
        opt = input("Qual operação deseja realizar?\n[ 1 ] Gerar arquivo .txt com as classificações\n[ 2 ] Mover os arquivos a pasta de cada categoria\n[ 0 ] Voltar ao menu principal\n\n")
        
        if opt == '1':
            Exportar4(classificacao)
    
        elif opt == '2':
            while True:
                opt2 = input("Esta operação irá mover os arquivos, e será preciso selecioná-los novamente para utilizar outra função. Deseja prosseguir? (s/n)\n")
                if opt2 == 's':
                    Mover(classificacao, vocabulario)
                    break
                elif opt2 == 'n':
                    break
                else:
                    continue
            
        elif opt == '0':
            break
        
    return None








#--------------------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
#--------------------------------------------------------------------------------------

mensagem = "\n\nEu sou um programa experimental, e não me responsabilizo por danos causados à máquina ou ao usuário.\nFaça backup dos seus arquivos antes de xeretar em mim.\n\n"
for letra in mensagem:
    sleep(0.015) # In seconds
    sys.stdout.write(letra)
    sys.stdout.flush()
    
sleep(2)

mensagem = "Primeiro, escolha um diretório de trabalho.\nOs textos não precisam necessariamente estar nele.\n\n"
for letra in mensagem:
    sleep(0.015) # In seconds
    sys.stdout.write(letra)
    sys.stdout.flush()

sleep(3)

global diretorio_trabalho
diretorio_trabalho = filedialog.askdirectory(title = "Escolha o diretório de trabalho")
os.chdir(diretorio_trabalho)

mensagem = "Agora, escolha os textos que quer utilizar.\n\n"
for letra in mensagem:
    sleep(0.015) # In seconds
    sys.stdout.write(letra)
    sys.stdout.flush()

sleep(2)

textos = CarregarTextos()

sleep(1)

Menu(textos)

mensagem = "\nObrigado por me usar!\n\nVisite nosso repositório no GitHub:\nhttps://github.com/MiqueiasSAraujo/economia_computacional.git\n"
for letra in mensagem:
    sleep(0.015) # In seconds
    sys.stdout.write(letra)
    sys.stdout.flush()