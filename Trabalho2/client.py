import sys
import select

from menu import *
from conexoes import *
from erros import *
from inputs import *
import estilo
import threading
import caixa_entrada

usuarioLogado = ""
usuariosAtivos = {}
conexoesAtivas = {}
chatAtivo = False
conexoes = [sys.stdin]
mutex = threading.Lock()
threads = []

# TODO: motrarJogadoresOnline
def mostrarUsuariosAtivos():
    """Mostra os usuários registrados no servidor central"""
    global usuariosAtivos
    usuariosAtivos = get_lista(usuarioLogado)

    #trata casos de nenhum usuario estar registrado
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    #mostra lista enumerada com usuarios ativos
    print(MSG_USUARIOS_ATIVOS)
    usernames = usuariosAtivos.keys()
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usernames)))
    print('\n')


# TODO: escolherAdversario
def escolherDestinatario():
    """Requisita escolha de destinatário para que o usuário
    inicie ou continue uma conversa"""

    mostrarUsuariosAtivos()

    #verificação para quando não há usuários registrados no servidpr
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    usuarioEscolhido = input(MSG_DESTINATARIO)

    while usuarioInvalido(usuarioEscolhido, usuariosAtivos):
        #cancela a abertura da conversa
        if usuarioEscolhido == "sair":
            return
        usuarioEscolhido = input(MSG_DESTINATARIO)

    return usuarioEscolhido

# TODO: digitarPalpite
def digitarNoChat(msg, envioSock, usuario):
    """Recebe a mensagem digitada pelo usuario, envia ao
    destinatario e registra na caixa de entrada"""

    msg_obj = {"username": usuarioLogado, "mensagem": msg}
    enviaMensagem(msg_obj, envioSock)

    mutex.acquire()
    caixa_entrada.registrarMensagem(usuario, msg_obj, True)
    mutex.release()

#TODO: iniciarPartida
def iniciaChat(envioSock, recebeSock, destinatario):
    """Representa a conversa corrente do usuario com outro,
    a tela do programa passa a só mostrar esta conversa até
    que o usuário digita fim para voltar ao menu"""

    global chatAtivo
    global conexoesAtivas
    global conexoes

    cls()

    mutex.acquire()

    #notifica o programa de que agora devera registra mensagens chegadas em foreground
    chatAtivo = True
    if envioSock not in conexoes:
        conexoes.append(envioSock)

    #remove notificação de mensagem para registrar como lida
    caixa_entrada.removeNotificacao(destinatario)
    mutex.release()

    while True:
        #mostra mensagens do usuario selecionado
        abrirConversa(destinatario)

        r, w, x = select.select(conexoes, [], [])
        for request in r:
            # caso algum cliente tente se conectar enquanto o usuario esta vendo as mensagens, se houver
            # pode ser o destinario ou outro cliente
            if request == recebeSock:
                sock_outro_cliente = aceitarNovaConexao(recebeSock)
                mutex.acquire()
                conexoes.append(sock_outro_cliente)
                mutex.release()

            # usuario envia mensagem para o destinatario
            elif request == sys.stdin:
                msg = input()

                if msg == 'fim':
                    fecharConversa()
                    return
                digitarNoChat(msg, envioSock, destinatario)

            else:
                #usuario recebe mensagem do usuario que esta conversando ou de outro
                data = recebeMensagem(request)

                if not data:
                    mutex.acquire()
                    encerrarConversa(request, conexoes)

                    usuarios = get_lista(usuarioLogado)
                    envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    envioSock.connect((usuarios[destinatario]["Endereco"], usuarios[destinatario]["Porta"]))
                    conexoesAtivas[destinatario] = envioSock
                    mutex.release()
                else:
                    mutex.acquire()

                    #verifica se a mensagem é do usuario com quem está conversando
                    visualizada = data["username"] == destinatario
                    caixa_entrada.registrarMensagem(data["username"], data, visualizada)
                    mutex.release()


def main():
    '''Funcao principal do cliente'''
    global usuarioLogado

    estilo.carregarHeader()

    # inicia o cliente para escutar
    sock_cliente, porta = prepararClienteParaEscuta()

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
            usuarioEscolhido, envioSock = pedeConexao()
            if usuarioEscolhido is None:
                continue

            # abre chat para conversa
            iniciaChat(envioSock, sock_cliente, usuarioEscolhido)

        elif cmd == 'sair':
            # encerra o programa
            sock_cliente.close()
            exit(0)
        else:
            comandoInvalido(cmd)

main()
