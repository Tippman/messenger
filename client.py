""" Клиентская часть """
from select import select
import sys
import socket
import threading
from lib.variables import *


class Client:
    def __init__(self, SERVER_ADDR):
        self.SERVER_ADDR = SERVER_ADDR
        self.nickname = input('Choose your nickname: ')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive(self):
        while True:
            try:
                message = self.client.recv(MAX_MSG_SIZE)
                message = message.decode(ENCODING_FORMAT)

                if message == 'NICK':
                    self.client.send(self.nickname.encode(ENCODING_FORMAT))
                else:
                    print(message)
            except:
                print('An error acured!')
                self.client.close()
                break

    def write(self):
        while True:
            try:
                message = input("")
                self.client.send(message.encode(ENCODING_FORMAT))
            except:
                sys.exit()

    def run(self):
        try:
            self.client.connect(self.SERVER_ADDR)
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            write_tread = threading.Thread(target=self.write)
            write_tread.start()
        except ConnectionRefusedError:
            print('Server unreachable!')


if __name__ == '__main__':
    client = Client(SERVER_ADDR)
    client.run()
