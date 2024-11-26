import socket
from threading import Thread

class Server:
    clients = []
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', 2024))
        self.socket.listen(2)

    def listen(self):
        while True:
            c_socket, address = self.socket.accept()
            print(f"Connection from: {address}")
            client = {'name': c_socket.recv(1024).decode(), 'socket': c_socket}
            Server.clients.append(client)
            Thread(target=self.handle_new_client, args=(client,)).start()

    def handle_new_client(self, client):
        c_name = client['name']
        c_socket = client['socket']
        while True:
            enc_message = c_socket.recv(1024).decode()
            print("Message from " + c_name + ": " + enc_message)
            for client in Server.clients:
                other_c_name = client['name']
                other_c_socket = client['socket']
                if other_c_name != c_name:
                    other_c_socket.send(enc_message.encode())

if __name__ == '__main__':
    Server().listen()
