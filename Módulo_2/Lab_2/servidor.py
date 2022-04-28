# servidor
import socket

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

def trataMsg(m):
    '''Funcao que recebe uma string m, tenta abrir o arquivo com o nome da string 
    e retorna uma string s com as 5 palavras de maior frequencia no arquivo'''
    D = {} # dicionario auxiliar
    s = '' # string de retorno
    try:
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
    except:
        raise FileNotFoundError
        s = 'FileNotFoundError'
    return s

# cria um socket para comunicacao
sock = socket.socket() # valores default: socket.AF_INET, socket.SOCK_STREAM  

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(5) 

# aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
print ('Conectado com: ', endereco)

while True:
        # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        msg = novoSock.recv(1024) # argumento indica a qtde maxima de dados
        if not msg: break 
        else:
            aux = (str(msg,  encoding='utf-8'))
            novaMsg = trataMsg(aux)
            # envia mensagem de resposta
            novoSock.send(bytes(novaMsg, 'utf-8'))
            if novaMsg == 'FileNotFoundError': break

# fecha o socket da conexao
novoSock.close() 

# fecha o socket principal
sock.close() 
