import sys
import select
import termo
from menu import *
from conexoes import *
from erros import *
from inputs import *

usuarioLogado = ""
serverSock = None
usuariosAtivos = {}
porta = 6005
STATUS = 'status'
entradas = [sys.stdin]

def mostrarUsuariosAtivos():
    """Mostra os usuários registrados no servidor central"""
    global usuariosAtivos
    global serverSock
    usuariosAtivos = get_lista(usuarioLogado, serverSock)
    usuariosDisponiveis = []
    
    #trata casos de nenhum usuario estar registrado
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    for usuario, info in usuariosAtivos.items():
        if info[STATUS] == 'disponivel':
            usuariosDisponiveis.append(usuario)

    #mostra lista enumerada com usuarios ativos
    print(MSG_USUARIOS_ATIVOS)
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usuariosDisponiveis)))
    print('\n')
    
    return usuariosDisponiveis

def escolherAdversario():
    """Requisita escolha de destinatário para que o usuário
    inicie ou continue uma conversa"""

    global serverSock

    usuariosDisponiveis = mostrarUsuariosAtivos()

    #verificação para quando não há usuários registrados no servidpr
    if len(usuariosDisponiveis) == 0:
        encerra()

    usuarioEscolhido = input(MSG_ADVERSARIO)

    while usuarioInvalido(usuarioEscolhido, usuariosAtivos):
        #cancela a abertura da conversa
        if usuarioEscolhido == "sair":
            return
        usuarioEscolhido = input(MSG_ADVERSARIO)

    # envia o adversário escolhido para o servidor
    msg = {'operacao': 'jogar','jogador': usuarioLogado, 'adversario': usuarioEscolhido}
    enviaMensagem(msg, serverSock)
    res = recebeMensagem(serverSock)
    if(res['status'] == 200):
        return res['idPartida'], res['primeiroJogador']
    elif(res['status'] == 401):
        print('Usuário indisponível')
        escolherAdversario()
        
    else:
        # trata erro
        encerra()

def recebeConvite():
    res = recebeMensagem(serverSock)
    jogador = res['jogador1']
    resposta = input(f'Você recebeu um convite para jogar com o jogador {jogador},\ndigite "sim" para aceitar e "não" para recusar: ')
    while resposta not in ['sim', 'não']:
        resposta = input(f'Você recebeu um convite para jogar com o jogador {jogador},\ndigite "sim" para aceitar e "não" para recusar: ')

    msg = {'resposta': resposta, 'status': 200}
    enviaMensagem(msg, serverSock)
    
    if resposta == 'não':
        encerra()
        
    server_res = recebeMensagem(serverSock)
    iniciarPartida(server_res['idPartida'], server_res['primeiroJogador'])

def enviarTentativa(tentativa, idPartida):
    """Recebe a mensagem digitada pelo usuario, envia ao
    destinatario e registra na caixa de entrada"""

    msg_obj = {"operacao": 'tentativa', "username": usuarioLogado, "tentativa": tentativa, 'idPartida': idPartida}
    enviaMensagem(msg_obj, serverSock)

def encerra():
    logoff(serverSock)
    serverSock.close()
    exit(0)

def displayTentativaAtual( res, tentativa ):
    tent = termo.analyzeWord( tentativa, res['palavra'])
    res['tentativas'].append( tent )
    termo.displayAttempts(res['tentativas'] )
    res['tentativas'].remove( tent )
    print( '*************\n')

def iniciarPartida(idPartida, primeiroJogador):
    possible_letters = [] + termo.alphabet
    if(primeiroJogador == usuarioLogado):  
        termo.printAlphabet( possible_letters )
        tentativa = termo.get_player_guess() 
        enviarTentativa(tentativa, idPartida)

    res = recebeMensagem(serverSock)
    while res['mensagem'] != 'fim':
        if len(res['tentativas']) >= 2:
            possible_letters = termo.reduceAlphabet( possible_letters, res['tentativas'][-2] )
        possible_letters = termo.reduceAlphabet( possible_letters, res['tentativas'][-1] )
        termo.displayAttempts(res['tentativas'] )
        termo.printAlphabet( possible_letters )
        tentativa = termo.get_player_guess() 
        displayTentativaAtual( res, tentativa )
        enviarTentativa(tentativa, idPartida)
        res = recebeMensagem(serverSock)

    termo.displayAttempts(res['tentativas'] )
    print('Jogo terminou!')
    if res['vencedor'] == usuarioLogado:
        print('Parabéns, você venceu!')
        
    elif(res['vencedor'] == 'tenteiro'):
        print('O jogo chegou ao seu limite de rodadas.')
        
    else:
        print('VoCê PeRdEu!!!!!')
    
    encerra()

def main():
    '''Funcao principal do cliente'''
    global usuarioLogado, serverSock, entradas
    
    while True:
        print('Digite um comando: ')
        r,w,x = select.select(entradas, [], [])
        for pronto in r:
            if pronto == serverSock:
                recebeConvite()
            elif pronto == sys.stdin:
                cmd = input()
                if cmd == 'login':
                    # registra o usuário no servidor
                    serverSock, usuarioLogado = login(porta)
                    entradas.append(serverSock)

                elif cmd == 'logoff':
                    # remove registro do servidor
                    usuarioLogado = logoff(serverSock)

                elif cmd == 'get_lista':
                    # mostra usuarios conectados ao servidor
                    mostrarUsuariosAtivos()

                elif cmd == 'jogar':
                    # requisita conexao com destinatario
                    idPartida, primeiroJogador = escolherAdversario()
                    
                    iniciarPartida(idPartida, primeiroJogador)

                elif cmd == 'sair':
                    # encerra o programa
                    serverSock.close()
                    exit(0)
                else:
                    comandoInvalido(cmd)

main()
