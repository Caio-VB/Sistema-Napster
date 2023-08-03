import socket, os, stat
from os import chdir, listdir
from os.path import isfile
import threading

class Peer:
    def __init__(self):
        self.ip = None
        self.porta = None
        self.pasta = None
        self.thread_processos = None
        
    # FUNÇÃO PARA OUVIR OUTROS PEERS
    def ouvir_peers(self):
        # INICIANDO O SOCKET PARA OUVIR OS OUTORS PEERS
        socket_p2p = socket.socket()
        socket_p2p.bind((self.ip, int(self.porta)))
        socket_p2p.listen(1)

        while True:
            # CONECTANDO COM OUTRO PEER
            conexao, addr = socket_p2p.accept()
            arquivo = conexao.recv(1024).decode()
            # VERIFICANDO SE TEM O ARQUIVO SOLICITADO
            if os.path.isfile(self.pasta+"\\"+arquivo):
                conexao.send(('ARQUIVO ENCONTRADO').encode())
                # LENDO E ENVIANDO O ARQUIVO EM PARTES
                with open(self.pasta + "\\" + arquivo, 'rb') as file:
                    for dados in file:
                        conexao.sendall(dados)
                conexao.close()
            else:
                conexao.send(('ARQUIVO NAO ENCONTRADO').encode())
                conexao.close()

    # INICIANDO A THREDING PARA OUVIR OUTROS PEERS
    def iniciar_thread(self):
        self.thread_processos = threading.Thread(target=self.ouvir_peers)
        self.thread_processos.start()
    
    # FECHANDO A THREDING PARA SAIR
    def encerrar_thread(self):
        self.thread_processos.join()

    # FUNÇÃO QUE SOLICITA O JOIN
    def join(self):
        conexao = socket.socket()
        conexao.connect(('127.0.0.1', 1099))
        # LISTANDO ARQUIVOS
        chdir(self.pasta)
        arquivos = ''
        for arq in listdir():
            if isfile(arq):
                arquivos = arquivos + ';@!' + arq
        # ENVIANDO REQUISIÇÃO JOIN
        conexao.send(('JOIN:;@!' + self.ip + ';@!' + self.porta + arquivos).encode())
        if conexao.recv(1024).decode() == 'JOIN_OK':
            arquivos = arquivos.replace(";@!", " ")
            print('Sou peer ' + self.ip + ':' + self.porta + ' com os arquivos' + arquivos)
            conexao.close()
            self.iniciar_thread()
        else:
            conexao.close()
        
    # FUNÇÃO QUE SOLICITA O SEARCH
    def search(self):
        conexao = socket.socket()
        conexao.connect(('127.0.0.1', 1099))
        arquivo = input("Digite o arquivo desejado: ")
        # ENVIANDO REQUISIÇÃO SEARCH
        conexao.send(('SEARCH:;@!' + self.ip + ';@!' + self.porta + ';@!' + arquivo).encode())
        print(conexao.recv(1024).decode())
        conexao.close()

    # FUNÇÃO QUE SOLICITA O DOWLOAD
    def dowload(self):
        ip_peer = input("Digite o IP do peer: ")
        porta_peer = input("Digite a porta do peer: ")
        arquivo = input("Digite o nome do arquivo desejado: ")
        try:
            conexao_p2p = socket.socket()
            conexao_p2p.connect((ip_peer, int(porta_peer)))
        except ConnectionRefusedError:
            pass
        else:
            # SOLICITANDO ARQUIVO AO PEER
            conexao_p2p.send(arquivo.encode())
            # RECEBENDO RESPOSTA DO PEER
            resposta = conexao_p2p.recv(1024).decode()
            if resposta == 'ARQUIVO NAO ENCONTRADO':
                print('O peer não possui o arquivo solicitado.')
            else:
                # RECEBENDO E JUNTANDO OS DADOS DO ARQUIVO
                with open(self.pasta + "\\" + arquivo, 'wb') as file:
                    while True:
                        data = conexao_p2p.recv(4096)
                        if not data:
                            break
                        file.write(data)
                    conexao_p2p.close()
                conexao_p2p.close()
                print('Dowload concluído')
                
                # FUNÇÃO QUE SOLICITA O UPDATE
                conexao = socket.socket()
                conexao.connect(('127.0.0.1', 1099))
                conexao.send(('UPDATE:;@!'+ self.ip + ';@!' + self.porta + ';@!' + arquivo).encode())
                conexao.recv(1024).decode()
                conexao.close()

    # FUNÇÃO QUE EXIBE O MENU
    def menu(self):
        print('Este é o menu interativo:')
        print('1. JOIN')
        print('2. SEARCH')
        print('3. DOWLOAD')
        print('4. SAIR')

    # FUNÇÃO QUE INICIA O PEER
    def iniciar(self):
        self.ip = input("Digite um IP para o peer: ")
        self.porta = input("Digite uma porta para o peer: ")
        self.pasta = input("Digite o caminho de uma pasta para o peer: ")
        while True:
            self.menu()
            opcao = input('Digite o número da opção desejada: ')
            if opcao == '1': # JOIN
                self.join()
            elif opcao == '2': # SEARCH
                self.search()
            elif opcao == '3': # DOWLOAD
                self.dowload()
            elif opcao == '4':
                break
        self.encerrar_thread()

peer = Peer()
peer.iniciar()
