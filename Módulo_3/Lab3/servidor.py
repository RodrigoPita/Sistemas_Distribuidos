#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading
import os
from colorama import Fore

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 5005 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena historico de conexoes 
conexoes = {}
#armazena os clientes na ordem de conexao
cliIndex = []
#lista de cores do ANSI
color_list = [Fore.RED, 
				Fore.GREEN, 
				Fore.YELLOW, 
				Fore.MAGENTA, 
				Fore.CYAN]

def iniciaServidor():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))

	# coloca-se em modo de espera por conexoes
	sock.listen(5) 

	# configura o socket para o modo nao-bloqueante
	sock.setblocking(False)

	# inclui o socket principal na lista de entradas de interesse
	entradas.append(sock)

	return sock

def aceitaConexao(sock):
	'''Aceita o pedido de conexao de um cliente
	Entrada: o socket do servidor
	Saida: o novo socket da conexao e o endereco do cliente'''

	# estabelece conexao com o proximo cliente
	clisock, endr = sock.accept()

	# registra a nova conexao
	conexoes[clisock] = endr 
	cliIndex.append(endr)

	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''
	cli_color = color_list[cliIndex.index(endr) % len(color_list)]
	while True:
		raw_aux, new_aux = '', '' 
		#recebe dados do cliente
		data = clisock.recv(1024) 
		raw_aux = str(data, encoding='utf-8')
		#verifica se o arquivo de nome raw_aux existe
		if os.path.exists(raw_aux):
			new_aux = trataMsg(raw_aux)
			data = new_aux.encode('utf-8')
			#clisock.send(bytes(new_aux, 'utf-8'))
		elif not data: # dados vazios: cliente encerrou
			print(cli_color + str(endr) + '-> encerrou')
			clisock.close() # encerra a conexao com o cliente
			return 
		else: print(cli_color + str(endr) + ': ' + str(data, encoding='utf-8'))
		clisock.send(data) # ecoa os dados para o cliente

def trataMsg(m):
	'''Funcao que recebe uma string m, tenta abrir o arquivo com o nome da string 
	e retorna uma string s com as 5 palavras de maior frequencia no arquivo'''
	D = {} # dicionario auxiliar
	s = '' # string de retorno
	for i in open(m):
		for j in i.strip() \
				.lower() \
				.replace(':', '') \
				.replace('.', '') \
				.replace(',', '') \
				.split():
			if j in D:
				D[j] += 1
			else:
				D[j] = 1    
	D_items = list(D.items()) # lista das tuplas (chave, valor) do dicionario
	L = [('', 0), ('', 0), ('', 0), ('', 0), ('', 0)]
	for k in D_items:
		if k[1] > L[0][1]:
			L[0] = k
		elif k[1] > L[1][1]:
			L[1] = k
		elif k[1] > L[2][1]:
			L[2] = k
		elif k[1] > L[3][1]:
			L[3] = k
		elif k[1] > L[4][1]:
			L[4] = k
	for i in L:
		s += (i[0] + ': ' + str(i[1]) + '\n')
	return s

def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	clientes=[] #armazena as threads criadas para fazer join
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	while True:
		#espera por qualquer entrada de interesse
		leitura, escrita, excecao = select.select(entradas, [], [])
		#tratar todas as entradas prontas
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = aceitaConexao(sock)
				print (Fore.WHITE + 'Conectado com: ', endr)
				#cria nova thread para atender o cliente
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr))
				cliente.start()
				clientes.append(cliente) #armazena a referencia da thread para usar com join()
			elif pronto == sys.stdin: #entrada padrao
				cmd = input()
				if cmd == 'fim': #solicitacao de finalizacao do servidor
					for c in clientes: #aguarda todas as threads terminarem
						c.join()
					sock.close()
					sys.exit()
				elif cmd == 'hist': #outro exemplo de comando para o servidor
					print(str(conexoes.values()))

main()