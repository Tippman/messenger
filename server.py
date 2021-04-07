""" Серверная часть """
import json
import sys
from icecream import ic
from select import select
import socket
import threading
import logging
import logs.config_server_log
from lib.variables import *
from lib.processors.receive_message_processor import MessageSplitter


class Server:
    def __init__(self, SERVER_ADDR):
        self.logger = logging.getLogger('server_log')
        self.SERVER_ADDR = SERVER_ADDR
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.msg_splitter = MessageSplitter()

        # self.nicknames = []

    def broadcast(self, message):
        """ отправляет сообщение всем участникам """
        for client in self.clients:
            client.send(message)

    def disconnect_socket(self, sock):
        """ отключает сокет"""
        # TODO как получить адрес клиента если он отключился?
        self.logger.info('Client disconnected')
        self.logger.info()
        index = self.clients.index(sock)
        nickname = self.nicknames[index]
        sock.close()
        self.clients.remove(sock)
        self.nicknames.remove(nickname)
        # self.broadcast(f'Client {nickname} disconnected!'.encode(ENCODING_FORMAT))

    def clients_read(self, r_sockets):
        """ читает данные из сокетов, от которыз поступили запросы  и возвращает словарь запросов"""
        responses = {}

        for sock in r_sockets:
            try:
                """ data = sock.recv(MAX_MSG_SIZE)
                data_str = data.decode(ENCODING_FORMAT)
                data_dict = json.loads(data_str)
                responses[sock] = data_dict """
                data = sock.recv(MAX_MSG_SIZE)  # читаем запакованные через struct данные

                # скармливаем данные с целью выполнить действия и сформировать ответ клиентам
                response = self.msg_splitter.feed(data)

                # если ответ получен в байтах значит не получено ошибки,
                # в противном случае получена ошибка и необходимо отклчить клиента
                if isinstance(bytes, response):
                    responses[sock] = response
                else:
                    if response['response'] == 400:
                        self.disconnect_socket(sock)

            except json.JSONDecodeError:
                self.logger.error('catch JSON Decoder error while reading clint request')
                # responses[sock] = data
            except:
                # удаляем сокет из переченя если клиент отключился
                self.disconnect_socket(sock)

        return responses

    def clients_write(self, responses, w_sockets):
        """ направляет ответы в сокеты, доступные для записи """
        for r_sock, data in responses.items():
            if not isinstance(bytes, data):
                ic(data)
            else:
                try:
                    for sock in w_sockets:
                        conn_info = sock.getpeername()
                        # если данные являются байтами - отправляем их клиенту
                        if r_sock != sock:
                            sock.send(data)

                            """ if data['action'] == 'on_chat':
                                sender_client_index = self.clients.index(r_sock)
                                sender_client_nickname = self.nicknames[sender_client_index]
                                sock.send(f'{sender_client_nickname}: {data["message"]}'.encode(ENCODING_FORMAT)) """
                            """if data.startswith('@'):
                                # если сообщение пользователя начинается с @
                                # проверяем кому оно адресовано, находим нужный сокет в clients и направляем туда сообщение
                                try:
                                    sender_client_index = self.clients.index(r_sock)
                                    sender_client_nickname = self.nicknames[sender_client_index]
                                    target_nickname, msg_clear_nickname = data.split(' ', maxsplit=1)

                                    if target_nickname[1:] in self.nicknames and target_nickname[
                                                                                 1:] != sender_client_nickname:
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
                                sock.send(data.encode(ENCODING_FORMAT))"""

                except:
                    # удаляем сокет из переченя если клиент отключился
                    self.disconnect_socket(sock)

    @staticmethod
    def is_auth_user(auth_response):
        return True

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

                # запрашиваем имя пользователя и пароль
                client.send('AUTH'.encode(ENCODING_FORMAT))
                auth_data = client.recv(MAX_MSG_SIZE)
                # todo авторизовать пользователя
                self.logger.info('Try to authenticate client %s', str(addr))
                auth_response = self.msg_splitter.feed(auth_data)
                client.send(auth_response)

                if self.is_auth_user(auth_response):
                    self.clients.append(client)

                """ nickname = auth_dict['user']['account_name']
                self.nicknames.append(nickname)

                print(f'Nicname of the client is {nickname}!')
                self.broadcast(f'{nickname} joined the chat!'.encode(ENCODING_FORMAT))
                client.send('Connected to the server'.encode(ENCODING_FORMAT)) """

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
                responses = self.clients_read(r_sockets)
                if responses:
                    self.clients_write(responses, w_sockets)


if __name__ == "__main__":
    server = Server(SERVER_ADDR)
    server.run()
