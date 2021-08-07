#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 5000 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena historico de conexoes 
conexoes = {}

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

	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''

	while True:
		#recebe dados do cliente
		msg = clisock.recv(1024) 
		if not msg: # dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			clisock.close() # encerra a conexao com o cliente
			return
		mensagem = str(msg, encoding='utf-8')

		# separa a mensagem em arquivo e palavra. Caso não consiga achar a palavra, significa que o comando fim foi executado, logo deve-se encerrar o socket atual
		arquivo = mensagem.split('\n')[0]
		try:
			palavra = mensagem.split('\n')[1]
		except:
			novoSock.close()
			novaConexao = True
			continue
		
		print("Mensagem recebida: {}".format(mensagem))
		print("Arquivo considerado: {}\nPalavra considerada: {}".format(arquivo, palavra))

		erro = False
		text = ""
		# Tenta ler o arquivo. Caso não consiga, a exceção disparada coloca a bool 'erro' como True.
		try:
			file = open(arquivo, "r")
			for line in file:
				text += line
		except:
			print("Erro ao ler arquivo")
			erro = True

		print("Mandando mensagem de volta para lado ativo!\n")
		
		# Retorna uma mensagem de erro em caso de erro, ou o número de ocorrências da palavra, em caso de êxito.
		if erro:
			clisock.send("Erro ao ler arquivo: arquivo não foi encontrado.".encode("utf-8"))
		else:
			clisock.send(str(text.count(palavra)).encode("utf-8"))
			
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
				print ('Conectado com: ', endr)
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