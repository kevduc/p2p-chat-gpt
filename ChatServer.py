import threading
import socket


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.nicknames = {}

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024).decode("utf-8")
                if message == "{quit}":
                    self.clients.remove(client)
                    client.close()
                    nickname = self.nicknames[client]
                    self.nicknames.remove(nickname)
                    self.broadcast(
                        f"{nickname} left the chat!".encode("utf-8"))
                    break
                else:
                    self.broadcast(message.encode("utf-8"))
            except:
                client.close()
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            client.send("NAMEREQUIRED".encode("utf-8"))
            nickname = client.recv(1024).decode("utf-8")
            if nickname in self.nicknames:
                client.send("NAMEEXISTS".encode("utf-8"))
                client.close()
            else:
                client.send("NAMEACCEPTED".encode("utf-8"))
                self.nicknames[client] = nickname
                self.clients.append(client)
                print(f"Nickname of client is {nickname}!")
                self.broadcast(f"{nickname} joined the chat!".encode("utf-8"))
                client.send("Connected to the server!".encode("utf-8"))
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()

    def start(self):
        print("Server Started!")
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()


if __name__ == "__main__":
    host = input("Enter host: ")
    port = int(input("Enter port: "))
    server = ChatServer(host, port)
    server.start()
