import os, time, json
from datetime import datetime

def limpa_tela():
    os.system("cls")

def aguarde(tempo):
    time.sleep(tempo)

def inicializarBancoDeDados():
    # r - read, w - write, a - append
    try:
        banco = open("base.data","r")
    except:
        print("Banco de Dados Inexistente. Criando...")
        banco = open("base.data","w")

def escreverDados(nome, pontos):
    # INI - inserindo no arquivo
    banco = open("base.data","r")
    dados = banco.read()
    banco.close()
    print("dados",type(dados))
    if dados != "":
        dadosDict = json.loads(dados)
    else:
        dadosDict = {}
        
    data_br = datetime.now().strftime("%d/%m/%Y")
    dadosDict[nome] = (pontos, data_br)
    
    banco = open("base.json","w")
    banco.write(json.dumps(dadosDict))
    banco.close()

