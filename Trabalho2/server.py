import select
import sys
import threading
import termo
from conexoes import *
import random

# define a localizacao do servidor
HOST = ''  # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 6010  # porta de acesso

partidas = {}
partida_id_count = 0



# define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
conexoes = {}
usuarios = {}

#campos json
OPERACAO = "operacao"
PORTA_MIN = "porta"
PORTA_MAI = "Porta"
ENDERECO_MIN = "endereco"
ENDERECO_MAI = "Endereco"
MENSAGEM = "mensagem"
STATUS = "status"
USERNAME = "username"
CLIENTES = "clientes"

#operacoes
LOGIN = "login"
LOGOFF = "logoff"
GET_LISTA = "get_lista"
JOGAR = "jogar"
TENTATIVA = "tentativa"

#mensagens
LOGIN_SUCESSO = "Login com sucesso"
LOGIN_INVALIDO = "Username em Uso"
LOGOFF_SUCESSO = "Logoff com sucesso"
LOGOFF_ERRO = "Erro no Logoff"

def iniciaServidor():
    """Cria um socket de servidor e o coloca em modo de espera por conexoes
    Saida: o socket criado"""

    # cria o socket com protocolo TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    """Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente"""

    # estabelece conexao com o proximo cliente
    clisock, endr = sock.accept()

    # registra a nova conexao
    #conexoes[clisock] = endr

    return clisock, endr


def atendeRequisicoes(clisock):
    """Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente"""
    print("VOU ATENDER A REQUISIÇÃO")
    
    # recebe dados do cliente
    data = recebeMensagem(clisock)
    print(data)
    if not data:  # dados vazios: cliente encerrou
        #print(str(endr) + '-> encerrou')
        clisock.close()  # encerra a conexao com o cliente
        return

    operacao = data[OPERACAO]

    if operacao == LOGIN:
        #TODO: incluir os status do usuario
        login(data[USERNAME], data[PORTA_MIN], clisock)
    elif operacao == LOGOFF:
        # remove registro do servidor
        # verifica se a requisição de logoff veio do proprio cliente
        # if conexoes[clisock] == endr:
        #     logoff(data[USERNAME], clisock)
        logoff(data[USERNAME], clisock)
    elif operacao == GET_LISTA:
        # retorn lista com usuarios ativos
        get_lista(clisock)
    elif operacao == JOGAR:
        print('recebi uma operacao de jogar')
        jogador1 = data['jogador']
        jogador2 = data['adversario']
        jogar(jogador1, jogador2)

        # TODO: incluir no JSON nome da pessoa a ser convidada,
        # TODO: enviar convite para o convidado, checar se o convidado já está jogando
        # TODO: receber aceitação e iniciar o jogo escolhendo o primeiro jogador, registrar a partida do lado do servidor com um id
        # TODO: enviar JSON "começou", com nome do primeiro jogador e id da partida
    elif operacao == TENTATIVA:
        processaTentativa(data)
        # TODO: receber no JSON o palpite com o nome do usuário que tentou
        # TODO: processar a tentativa 
        # TODO: retornar a palavra com os caracteres de coloração e com nome do jogar que tentou
        # TODO: se a tentiva for correta envia "fim", com nome do ganhador.
        pass


def login(username, porta, clisock, endr=[0, 1]):
    """Registra o usuario na lista do servidor"""
    if (username in usuarios):
        mensagem = {OPERACAO: LOGIN, STATUS: 400,
                    MENSAGEM: LOGIN_INVALIDO}
        enviaMensagem(mensagem, clisock)
    else:
        usuarios[username] = {ENDERECO_MAI: endr[0], PORTA_MAI: porta, STATUS: 'disponivel'}
        mensagem = {OPERACAO: LOGIN, STATUS: 200,
                    MENSAGEM: LOGIN_SUCESSO}
        # registra nova conexão
        conexoes[username] = clisock
        enviaMensagem(mensagem, clisock)


def get_lista(client_sock):
    """Rertorna lista com usuarios ativos"""
    mensagem = {OPERACAO: GET_LISTA, STATUS: 200, CLIENTES: usuarios}
    enviaMensagem(mensagem, client_sock)


def logoff(username, clisock):
    """Remove usuario da lista de usuairos ativos do servidor"""
    if (username not in usuarios):
        mensagem = {OPERACAO: LOGOFF, STATUS: 400,
                    MENSAGEM: LOGOFF_ERRO}
        enviaMensagem(mensagem, clisock)
    else:
        del usuarios[username]
        del conexoes[username]
        mensagem = {OPERACAO: LOGOFF, STATUS: 200,
                    MENSAGEM: LOGOFF_SUCESSO}
        enviaMensagem(mensagem, clisock)

def getEndereco(usuario):
    usuarios = get_lista(conexoes[usuario])
    for usr in usuarios:
        if usr == usuario and usr[STATUS] == 'disponivel':
            return (usr[ENDERECO_MAI], usr[PORTA_MAI])  
        else:
            return None

def enviaPalavra(jogador, primeiroJogador, idPartida):
    msg = {'primeiroJogador': primeiroJogador, 'status': 200, 'idPartida': idPartida}
    sock = conexoes[jogador]
    enviaMensagem(msg, sock)

def registrarPartida(palavra, jogador1, jogador2):
    global partida_id_count
    res = partida_id_count
    partidas[partida_id_count] = {'palavra': palavra, 'jogador1': jogador1, 'jogador2': jogador2, 'tentativas': []}
    partida_id_count += 1
    return res


def jogar(jogador1, jogador2):
    print('entrei no JOGAR')
    jogadores = [jogador1, jogador2]

    sock_jogador2 = conexoes[jogador2]
    msg = {'operacao': 'convite', 'jogador1': jogador1}
    print(f'vou enviar o convite da {jogador1} para o {jogador2}')
    enviaMensagem(msg, sock_jogador2)
    print(msg)
    res = recebeMensagem(sock_jogador2)
    print(res)
    if(res[STATUS] == 200):
        if(res['resposta'] == 'sim'):

            # envia a palavra escolhida para os dois jogadores
    
            # escolhe uma palavra para o jogo
            palavra = termo.chooseWord(termo.playable_words)

            # escolhe o primeiro jogador
            primeiroJogador = random.randint(0,1)
            print(f"primeiro jogador: {primeiroJogador}")
            partida_id = registrarPartida(palavra, jogador1, jogador2)

            enviaPalavra(jogador1, jogadores[primeiroJogador], partida_id)
            enviaPalavra(jogador2, jogadores[primeiroJogador], partida_id)
            
            return partida_id
        else:
            # tratar Não
            pass
    else:
        # tratar erro
        pass



# tenteiro: jogador que fez o chute
def processaTentativa(data):
    tentativa = data['tentativa']
    partidaId = data['idPartida']
    tenteiro = data['username']
    jogador1 = partidas[partidaId]['jogador1']
    jogador2 = partidas[partidaId]['jogador2']
    palavra = partidas[partidaId]['palavra']
    res = termo.analyzeWord(tentativa, palavra)
    partidas[partidaId]['tentativas'].append(res)


    sock_jogador1 = conexoes[jogador1]
    sock_jogador2 = conexoes[jogador2]

    if(tentativa == palavra):
        msg = {'mensagem': 'fim', 'vencedor': tenteiro}
        enviaMensagem(msg, sock_jogador1)
        enviaMensagem(msg, sock_jogador2)

    msg = {'mensagem': 'continua','tentativas': partidas[partidaId]['tentativas'], 'tenteiro': tenteiro}

    if(tenteiro == jogador2):
        enviaMensagem(msg, sock_jogador1)
    else:
        enviaMensagem(msg, sock_jogador2)

    



    
    

def main():
    """Inicializa e implementa o loop principal (infinito) do servidor"""
    clientes = []  # armazena as threads criadas para fazer join
    sock = iniciaServidor()
    print("Pronto para receber conexoes...")
    while True:
        # espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        # tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == sock:  # pedido novo de conexao
                
                clisock, endr = aceitaConexao(sock)
                entradas.append(clisock)
                print('Conectado com: ', endr)
                # cria nova thread para atender o cliente
                # cliente = threading.Thread(
                #     target=atendeRequisicoes, args=(clisock, endr, sock))

                #cliente.start()
                # armazena a referencia da thread para usar com join()
                #clientes.append(cliente)
            elif pronto == sys.stdin:  # entrada padrao
                cmd = input()
                if cmd == 'fim':  # solicitacao de finalizacao do servidor
                    for c in clientes:  # aguarda todas as threads terminarem
                        c.join()
                    sock.close()
                    sys.exit()
                elif cmd == 'hist':  # outro exemplo de comando para o servidor
                    print(str(conexoes.values()))
            else:
                atendeRequisicoes(pronto)

main()
