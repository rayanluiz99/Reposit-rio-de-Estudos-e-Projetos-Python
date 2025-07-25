import socket

HOST = 'localhost'
PORT = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((HOST, PORT))

sock.send('enviado'.encode())

confirmacao = sock.recv(1024).decode()
if confirmacao == 'ok':
    print('mensagem recebida')