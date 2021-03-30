""" Серверная часть """
import sys
from select import select
import socket
import threading
from lib.variables import *


class Server:
    def __init__(self, SERVER_ADDR):
        self.SERVER_ADDR = SERVER_ADDR
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.nicknames = []

    def broadcast(self, message):
        """ отправляет сообщение всем участникам """
        for client in self.clients:
            client.send(message)

    def disconnect_socket(self, sock):
        """ отключает сокет"""
        index = self.clients.index(sock)
        nickname = self.nicknames[index]
        sock.close()
        self.clients.remove(sock)
        self.nicknames.remove(nickname)
        self.broadcast(f'Client {nickname} disconnected!'.encode(ENCODING_FORMAT))

    def clients_read(self, r_sockets):
        """ читает данные из сокетов, от которыз поступили запросы  и возвращает словарь запросов"""
        requests = {}

        for sock in r_sockets:
            try:
                data = sock.recv(MAX_MSG_SIZE).decode(ENCODING_FORMAT)
                requests[sock] = data
            #     TODO сейчас сообщения никуда не скармливаются для обработки. В дальнейшем они будут уходить в receive_message_processor
            except:
                # удаляем сокет из переченя если клиент отключился
                self.disconnect_socket(sock)

        return requests

    def clients_write(self, requests, w_sockets):
        """ направляет ответы в сокеты, доступные для записи """
        for sock in w_sockets:
            try:
                for r_sock, data in requests.items():
                    if r_sock != sock:

                        # TODO скормить данные для обратоки (json)
                        if data.startswith('@'):
                            # если сообщение пользователя начинается с @
                            # проверяем кому оно адресовано, находим нужный сокет в clients и направляем туда сообщение
                            try:
                                sender_client_index = self.clients.index(r_sock)
                                sender_client_nuckname = self.nicknames[sender_client_index]
                                target_nickname, msg_clear_nickname = data.split(' ', maxsplit=1)

                                if target_nickname[1:] in self.nicknames and target_nickname[
                                                                             1:] != sender_client_nuckname:
                                    target_index = self.nicknames.index(target_nickname[1:])
                                    target_client = self.clients[target_index]
                                    if sock == target_client:
                                        target_client.send(msg_clear_nickname.encode(ENCODING_FORMAT))

                                else:
                                    r_sock.send(
                                        f'there is no user with nickname {target_nickname}'.encode(ENCODING_FORMAT))
                            except ValueError:
                                r_sock.send(f'Enter a message to user {data}'.encode(ENCODING_FORMAT))
                            except:
                                print(f'Something wrong!')

                        else:
                            sock.send(data.encode(ENCODING_FORMAT))

            except Exception as e:
                # удаляем сокет из переченя если клиент отключился
                # TODO delete raising exception
                self.disconnect_socket(sock)
                raise

    def run(self):
        """ основной поток обработки входящих соединений """
        print('Server is listening...')

        self.server.bind(self.SERVER_ADDR)
        self.server.listen(MAX_CONNECTIONS)
        self.server.settimeout(0.2)

        while True:
            try:
                client, addr = self.server.accept()
                print(f'Connetcted with {str(addr)}')

                # запрашиваем имя пользователя
                client.send('NICK'.encode(ENCODING_FORMAT))
                nickname = client.recv(MAX_MSG_SIZE).decode(ENCODING_FORMAT)
                self.clients.append(client)
                self.nicknames.append(nickname)

                print(f'Nicname of the client is {nickname}!')
                self.broadcast(f'{nickname} joined the chat!'.encode(ENCODING_FORMAT))
                client.send('Connected to the server'.encode(ENCODING_FORMAT))

            except OSError:
                pass
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(e)
            finally:
                r_sockets = []
                w_sockets = []
                try:
                    r_sockets, w_sockets, e = select(self.clients, self.clients, [], 0)
                except:
                    pass  # ничего не делать если клиент отключился
                requests = self.clients_read(r_sockets)
                if requests:
                    self.clients_write(requests, w_sockets)


if __name__ == "__main__":
    server = Server(SERVER_ADDR)
    server.run()
