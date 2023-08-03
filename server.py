import socket

class Servidor:
    def __init__(self):
        self.ip = None
        self.porta = None
        self.servidor_socket = None
        self.repositorio = []

    # FUNÇÃO QUE EXECUTA JOIN
    def join(self, conexao, addr, requisicao):
        del requisicao[0:3]
        arquivos = ';@!'.join(str(elemento) for elemento in requisicao)
        conexao.send('JOIN_OK'.encode())
        self.repositorio.append((addr + ';@!' + arquivos).split(';@!'))
        arquivos = arquivos.replace(";@!", " ")
        print ('Peer', addr, 'adicionado com arquivos', arquivos)

    # FUNÇÃO QUE EXECUTA SEARCH
    def search(self, conexao, addr, requisicao):
        arquivo = requisicao[3]
        print('Peer ' + addr + ' solicitou o arquivo ' + arquivo)
        peers = ['peers com o arquivo:']

        for peer in self.repositorio:
            for titulo in peer:
                if titulo == arquivo and titulo != peer[0] and peer[0] != addr:
                    peers.append(peer[0])

        peers = ' '.join(peers)
        conexao.send(peers.encode())

    # FUNÇÃO QUE EXECUTA UPDATE
    def update(self, conexao, addr, requisicao):
        arquivo_novo = requisicao[3]

        for peer in self.repositorio:
            if peer[0] == addr:
                peer.append(arquivo_novo)

        conexao.send('UPDATE_OK'.encode())

    # FUNÇÃO QUE INICIA O SERVER
    def iniciar(self):
        self.ip = input("Digite o IP do server: ")
        self.porta = input("Digite a porta do server: ")
        self.repositorio = []

        # INICIANDO O SOCKET PARA OUVIR OS PEERS
        self.servidor_socket = socket.socket()
        self.servidor_socket.bind((self.ip, int(self.porta)))
        self.servidor_socket.listen(20)

        while True:
            # CONECTANDO COM O PEER
            conexao, addr = self.servidor_socket.accept()

            # LENDO A REQUISIÇÃO E DIRECIONANDO PARA O SERVIÇO CORRETO
            requisicao = conexao.recv(1024).decode()
            requisicao = requisicao.split(';@!')
            addr = requisicao[1] + ":" + requisicao[2]
            if requisicao[0] == 'JOIN:':
                self.join(conexao, addr, requisicao)
            elif requisicao[0] == 'SEARCH:':
                self.search(conexao, addr, requisicao)
            elif requisicao[0] == 'UPDATE:':
                self.update(conexao, addr, requisicao)

            conexao.close()

servidor = Servidor()
servidor.iniciar()