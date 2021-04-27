""" Клиентская часть """
import json
from queue import Queue
from select import select
import sys
import socket
import threading
import datetime
import struct
import logging

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

import logs.config_server_log
from icecream import ic

from gui.client_chat_gui import MainChatWindow
from gui.client_login_gui import MainLoginWindow
from gui.gui_event_handlers import UiNotifier
from lib.processors.client_message_factory.client_message_factory import ClientMessageFactory
from lib.processors.receive_message_processor import MessageSplitter
from lib.processors.message_sender import Serializer
from lib.variables import *


class Client:
    def __init__(self,
                 SERVER_ADDR=None,
                 client_message_factory=ClientMessageFactory(),
                 serializer=Serializer(),
                 ui_notifier=None):
        self.SERVER_ADDR = SERVER_ADDR
        self.client_msg_factory = client_message_factory
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.msg_splitter = MessageSplitter()
        self.login = ''
        self.password = ''
        self.client_ip = ''
        self.client_port = int

        self.logger = logging.getLogger('client_log')

        self.serializer = serializer
        self.client_queue = Queue()
        self.client_thr_killer = threading.Event()
        self.ui_notifier = ui_notifier

    def disconnect(self):
        self.client_thr_killer.set()
        self.client.close()

    def receive(self, stopper):
        while not stopper.is_set():
            try:
                message = self.client.recv(MAX_MSG_SIZE)

                if message == 'AUTH'.encode(ENCODING_FORMAT):
                    self.logger.info('%s: Receive auth response from server', str(self.client.getsockname()))

                    auth_dict = self.client_msg_factory.create_auth_message(self.login, self.password)
                    auth_data = self.serializer.pack_data(auth_dict, self.client_ip, self.client_port)
                    self.client.send(auth_data)
                    self.client.send(self.login.encode(ENCODING_FORMAT))

                elif message == 'GET_CONTACTS'.encode(ENCODING_FORMAT):
                    self.logger.info('%s: Requesting client contact list', str(self.client.getsockname()))

                    request_dict = self.client_msg_factory.create_request_get_client_contacts(self.login)
                    request_data = self.serializer.pack_data(request_dict, self.client_ip, self.client_port)
                    self.client.send(request_data)

                else:
                    # если получен ответ от сервера - передаем его обработчику
                    self.logger.info('Client receive msg from server.')
                    self.msg_splitter.feed(message, self.ui_notifier)
            except OSError:
                pass
            except Exception as e:
                self.logger.error('Client catch an error: %s', e)
                self.disconnect()

    def write(self, stopper):
        while not stopper.is_set():
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
                self.disconnect()

    def run(self):
        try:
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client.connect(self.SERVER_ADDR)
            self.client_ip, self.client_port = self.client.getsockname()

            receive_thread = threading.Thread(target=self.receive, args=(self.client_thr_killer,))
            receive_thread.start()

            # write_tread = threading.Thread(target=self.write, args=(self.client_thr_killer,))
            # write_tread.start()

            client_queue_handler = threading.Thread(target=self.client_queue_handler)
            client_queue_handler.start()

        except ConnectionRefusedError:
            print('Server unreachable!')
        except:
            raise

    def client_queue_handler(self):
        """ обработка очереди клиента. Очередь пополняется из GUI """
        while not self.client_thr_killer.is_set():
            if not self.client_queue.empty():
                queue_item = self.client_queue.get_nowait()
                if isinstance(queue_item, dict):
                    try:
                        action = queue_item['action']
                        if action in ACTION_LIST and action == 'p2p':
                            request_dict = self.client_msg_factory.create_p2p_msg(target=queue_item['target'],
                                                                   msg=queue_item['msg'],
                                                                   author=self.login)
                            data = self.serializer.pack_data(request_dict, self.client_ip, self.client_port)
                            self.client.send(data)
                            self.logger.debug('sending p2p request')

                    except KeyError:
                        self.logger.debug('Error while getting a key from a queue item')


if __name__ == '__main__':
    # client.run()

    # client_main_loop = threading.Thread(target=client.run())
    # client_main_loop.start()

    client_login_app = QApplication(sys.argv)
    ui_notifier = UiNotifier(app=client_login_app)
    client = Client(ui_notifier=ui_notifier)
    login_window = MainLoginWindow(client)
    ui_notifier.receiver = login_window
    login_window.show()
    client_login_app.exec_()

    client_chat_app = QApplication(sys.argv)
    ui_notifier.app = client_chat_app
    chat_window = MainChatWindow(client)
    ui_notifier.receiver = chat_window
    chat_window.show()
    client_chat_app.exec_()
