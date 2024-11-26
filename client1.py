import socket
from threading import Thread
import index_key
from pka import main_key

class Client:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect(('127.0.0.1', 2024))
        self.talk_to_server()

    def talk_to_server(self):
        self.socket.send('client1'.encode())
        Thread(target = self.receive_message).start()
        self.send_message()

    def send_message(self):
        while True:
            client_input = input('')
            enc_message = index_key.encrypt(client_input.encode('utf-8').hex(), index_key.key(main_key(1)))
            self.socket.send(enc_message.encode())

    def receive_message(self):
        while True:
            enc_message = self.socket.recv(1024).decode()
            server_inbox = bytes.fromhex(index_key.decrypt(enc_message, index_key.key(main_key(2)))).decode('utf-8')
            print('Inbox: ' + server_inbox)

if __name__ == '__main__':
    Client()
