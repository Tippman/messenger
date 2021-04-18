""" Клиентская часть """
import json
from select import select
import sys
import socket
import threading
import datetime
import struct
import logging

from PyQt5.QtWidgets import QApplication

import logs.config_server_log
from icecream import ic

from gui.client_login_gui import MainLoginWindow
from lib.processors.client_message_factory.client_message_factory import ClientMessageFactory
from lib.processors.receive_message_processor import MessageSplitter
from lib.processors.message_sender import Serializer
from lib.variables import *


class Client:
    def __init__(self, SERVER_ADDR, client_message_factory=ClientMessageFactory(), serializer=Serializer()):
        self.SERVER_ADDR = SERVER_ADDR
        self.client_msg_factory = client_message_factory
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.msg_splitter = MessageSplitter()
        self.login = 'tippman'
        self.password = 's1234'
        self.client_ip = ''
        self.client_port = int
        self.logger = logging.getLogger('client_log')
        self.serializer = serializer

    def receive(self):
        while True:
            try:
                message = self.client.recv(MAX_MSG_SIZE)

                if message == 'AUTH'.encode(ENCODING_FORMAT):
                    self.logger.info('%s: Receive auth response from server', str(self.client.getsockname()))

                    auth_dict = self.client_msg_factory.create_auth_message(self.login, self.password)
                    auth_data = self.serializer.pack_data(auth_dict, self.client_ip, self.client_port)
                    self.client.send(auth_data)

                elif message == 'GET_CONTACTS'.encode(ENCODING_FORMAT):
                    self.logger.info('%s: Requesting client contact list', str(self.client.getsockname()))

                    request_dict = self.client_msg_factory.create_request_get_client_contacts(self.login)
                    request_data = self.serializer.pack_data(request_dict, self.client_ip, self.client_port)
                    self.client.send(request_data)

                else:
                    # если получен ответ от сервера - передаем его обработчику
                    self.logger.info('Client receive msg from server.')
                    self.msg_splitter.feed(message)
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
                        data = self.serializer.pack_data(get_message_data, self.client_ip, self.client_port)
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
            self.client_ip, self.client_port = self.client.getsockname()

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

            write_tread = threading.Thread(target=self.write)
            write_tread.start()
        except ConnectionRefusedError:
            print('Server unreachable!')


if __name__ == '__main__':
    client = Client(SERVER_ADDR)

    client_login_app = QApplication(sys.argv)
    mw = MainLoginWindow()
    mw.show()
    client_main_loop = threading.Thread(target=client.run())
    sys.exit(client_login_app.exec_())
