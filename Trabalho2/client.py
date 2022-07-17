import sys
import select
import termo
from menu import *
from conexoes import *
from erros import *
from inputs import *
import estilo
import threading

usuarioLogado = ""
usuariosAtivos = {}
conexoesAtivas = {}
chatAtivo = False
conexoes = [sys.stdin]
mutex = threading.Lock()
threads = []
porta = 6004

# TODO: motrarJogadoresOnline
def mostrarUsuariosAtivos():
    """Mostra os usuários registrados no servidor central"""
    global usuariosAtivos
    usuariosAtivos = get_lista(usuarioLogado)
    usuariosDisponiveis = []
    
    #trata casos de nenhum usuario estar registrado
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    for usuario in usuariosAtivos:
        if usuario['STATUS'] == 'disponivel':
            usuariosDisponiveis.append(usuario)

    #mostra lista enumerada com usuarios ativos
    print(MSG_USUARIOS_ATIVOS)
    usernames = usuariosDisponiveis.keys()
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usernames)))
    print('\n')

# TODO: escolherAdversario
def escolherAdversario():
    """Requisita escolha de destinatário para que o usuário
    inicie ou continue uma conversa"""

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
    sock = connectWithCentralServer()
    msg = {'operacao': 'jogar','jogador': usuarioLogado, 'adversario': usuarioEscolhido}
    enviaMensagem(msg, sock)
    res = recebeMensagem(sock)
    

    return res

# TODO: digitar Tentativa
def enviarTentativa(msg):
    """Recebe a mensagem digitada pelo usuario, envia ao
    destinatario e registra na caixa de entrada"""

    sock = connectWithCentralServer()
    msg_obj = {"operacao": 'tentativa', "username": usuarioLogado, "tentativa": msg}
    enviaMensagem(msg_obj, sock)

    res = recebeMensagem(sock)
    return res


def process_rounds_guess(chosen_word):
    attempts = []
    possible_letters = [] + termo.alphabet
    for round in range( 1, termo.MAX_ROUNDS+1 ):
        termo.printAlphabet( possible_letters )
        guess = termo.get_player_guess(round)
        if ( round == 1 ): start = termo.time()
        result = enviarTentativa( guess )
        possible_letters = termo.reduceAlphabet( possible_letters, result['tentativas'][:-1] )
        termo.displayAttempts( chosen_word, result['tentativas'], round )
        if ( guess == chosen_word ): break
    return round, start, guess


#TODO: iniciarPartida
def iniciarPartida(palavra):
    '''Da inicio ao jogo'''
    palavra_display = termo.get_displayable_format(palavra)
    final_round, start, guess = process_rounds_guess(palavra)
    termo.finalMessage( guess, palavra ,palavra_display, final_round, start )


def main():
    '''Funcao principal do cliente'''
    global usuarioLogado

    estilo.carregarHeader()

    # inicia o cliente para escutar
    #sock_cliente, porta = prepararClienteParaEscuta()

    while True:
        cmd = input("Digite um comando: ")
        if cmd == 'login':
            # registra o usuário no servidor
            usuarioLogado = login(porta)

        elif cmd == 'logoff':
            # remove registro do servidor
            usuarioLogado = logoff()

        elif cmd == 'get_lista':
            # mostra usuarios conectados ao servidor
            mostrarUsuariosAtivos()

        elif cmd == 'jogar':
            # requisita conexao com destinatario
            palavra = escolherAdversario()
            
            iniciarPartida(palavra)

        elif cmd == 'sair':
            # encerra o programa
            sock_cliente.close()
            exit(0)
        else:
            comandoInvalido(cmd)

main()
