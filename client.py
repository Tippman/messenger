""" Клиентская часть """
import json
from select import select
import sys
import socket
import threading
import datetime
import struct
import logging
import logs.config_server_log
from icecream import ic

from lib.processors.client_message_factory.client_message_factory import ClientMessageFactory
from lib.processors.receive_message_processor import MessageSplitter
from lib.variables import *


class Client:
    def __init__(self, SERVER_ADDR, client_message_factory=ClientMessageFactory()):
        self.SERVER_ADDR = SERVER_ADDR
        self.client_msg_factory = client_message_factory
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.msg_splitter = MessageSplitter()
        self.logger = logging.getLogger('client_log')

    def pack_data(self, data):
        """ упаковывает данные с заголовками:
         | msg len: 2b | client ip: 4b | client port: 2b | msg_dict: 1024 - 8b |
         возвращает bytes (struct) """
        msg_dict_pack = json.dumps(data).encode(ENCODING_FORMAT)
        client_ip, client_port = self.client.getpeername()
        return struct.pack(PACK_FORMAT,
                           len(msg_dict_pack),  # длина отправляемого сообщения (словаря с запросом)
                           ipaddress.IPv4Address(client_ip).packed,
                           client_port,
                           msg_dict_pack)  # сам словарь с запросом

    def receive(self):
        while True:
            try:
                message = self.client.recv(MAX_MSG_SIZE)

                if message == 'AUTH'.encode(ENCODING_FORMAT):
                    self.logger.info('%s: Receive auth response from server', str(self.client.getpeername()))
                    login = 'tippman'
                    password = '1234'
                    auth_dict = self.client_msg_factory.create_auth_message(login, password)
                    auth_data = self.pack_data(auth_dict)
                    self.client.send(auth_data)
                else:
                    # если получен ответ от сервера - передаем его обработчику
                    self.logger.info('Client receive msg from server')
                    proceed_server_response = self.msg_splitter.feed(message)
            except Exception as e:
                self.logger.error('Client catch an error: %s', e)
                self.client.close()
                break

    def write(self):
        while True:
            try:
                message = input("")
                # если сообщение начинается с "решетки" значит это команда
                if message.startswith('#'):
                    # формируется соответствующий словарь
                    # если get_message_data is None значит команда была введена неправильно
                    get_message_data = self.client_msg_factory.feed(message)
                    if get_message_data:
                        data = self.pack_data(get_message_data)
                        self.client.send(data)
                    else:
                        print('Enter a correct command / message')
                else:
                    print('Message must starts with "@" - for p2p, or "#" - for command.')
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
