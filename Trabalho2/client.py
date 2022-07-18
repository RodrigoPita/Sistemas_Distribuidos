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

# TODO: motrarJogadoresOnline
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

# TODO: escolherAdversario
def escolherAdversario():
    """Requisita escolha de destinatário para que o usuário
    inicie ou continue uma conversa"""

    global serverSock

    mostrarUsuariosAtivos()

    #verificação para quando não há usuários registrados no servidpr
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

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
    else:
        # trata erro
        pass

def recebeConvite():
    print('recebi convite')
    res = recebeMensagem(serverSock)
    print(res)
    jogador = res['jogador1']
    resposta = input(f'Você recebeu um convite para jogar com o jogador {jogador}, digite "sim" para aceitar e "não" para recusar.')
    if resposta not in ['sim', 'não']:
        # resposta não é válida
        pass
    else:
        msg = {'resposta': resposta, 'status': 200}
        enviaMensagem(msg, serverSock)

        server_res = recebeMensagem(serverSock)
        print(server_res)
        iniciarPartida(server_res['idPartida'], server_res['primeiroJogador'])


# TODO: digitar Tentativa
def enviarTentativa(tentativa, idPartida):
    """Recebe a mensagem digitada pelo usuario, envia ao
    destinatario e registra na caixa de entrada"""

    msg_obj = {"operacao": 'tentativa', "username": usuarioLogado, "tentativa": tentativa, 'idPartida': idPartida}
    enviaMensagem(msg_obj, serverSock)

def encerra():
    logoff(serverSock)
    serverSock.close()
    exit(0)

#TODO: iniciarPartida
'''
def iniciarPartida(palavra):
    # Da inicio ao jogo
    palavra_display = termo.get_displayable_format(palavra)
    final_round, start, guess = process_rounds_guess(palavra)
    termo.finalMessage( guess, palavra ,palavra_display, final_round, start )

'''



def iniciarPartida(idPartida, primeiroJogador):
    print("INICIEI A PARTIDA")
    #tentativas = []
    possible_letters = [] + termo.alphabet
    if(primeiroJogador == usuarioLogado):  
        termo.printAlphabet( possible_letters )
        tentativa = termo.get_player_guess() 
        #tentativas.append(tentativa)
        enviarTentativa(tentativa, idPartida)

    res = recebeMensagem(serverSock)
    
    while res['mensagem'] != 'fim':
        if len(res['tentativas']) >= 2:
            possible_letters = termo.reduceAlphabet( possible_letters, res['tentativas'][-2] )
        possible_letters = termo.reduceAlphabet( possible_letters, res['tentativas'][-1] )
        termo.displayAttempts(res['tentativas'] )
        termo.printAlphabet( possible_letters )
        tentativa = termo.get_player_guess() 
        enviarTentativa(tentativa, idPartida)
        res = recebeMensagem(serverSock)

    termo.displayAttempts(res['tentativas'] )
    print('Jogo terminou!')
    if res['vencedor'] == usuarioLogado:
        print('Parabéns, você venceu!')
    else:
        print('VoCê PeRdEu!!!!!')
    
    encerra()

def main():
    '''Funcao principal do cliente'''
    global usuarioLogado, serverSock, entradas
    
    # inicia o cliente para escutar
    #sock_cliente, porta = prepararClienteParaEscuta()

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
