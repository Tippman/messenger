from sqlalchemy.orm import sessionmaker

from lib.processors.disconnector import Disconnector
from lib.processors.message_dataclasses import *
from db.client_db import ClientStorage
from lib.variables import ENGINE


class ServerMessageHandler:
    # обработка сообщений от клиента на сервере
    def __init__(self, disconnector=Disconnector()):
        self._disconnector = disconnector

    def on_chat(self, dataclass):
        pass

    def authenticate_client(self, dataclass):
        Session = sessionmaker(bind=ENGINE)
        session = Session()
        client_storage = ClientStorage(session)
        if client_storage.is_client_exist(dataclass.account_name):
            if client_storage.check_auth_data(dataclass.account_name, dataclass.password):
                # если найдено совпадение логина и пароля - формируем ответ 200 клиенту
                # TODO create answer to client
                pass

    def register(self, dataclass):
        pass


    def unregister(self, dataclass):
        pass

    def on_peer(self, dataclass):
        pass

    def on_unhandled_msg(self, dataclass, ip_addr, port):
        self._disconnector.disconnect(ip_addr, port, 'unhandled server routing')


class ClientMessageHandler:
    # обработка сообщений от сервера на склиенте
    def status_200(self, dataclass):
        pass

    def status_400(self, dataclass):
        pass


class MessageRouter:
    """ Роутер сообщений. принимает dataclasses и направляет их в соответствующий обработчик
        ServerHandler или ClientHandler """

    def __init__(self,
                 server_msg_handler=ServerMessageHandler(),
                 client_msg_handler=ClientMessageHandler(),
                 disconnector=Disconnector()):
        self.server_msg_handler = server_msg_handler
        self.client_msg_handler = client_msg_handler

    def on_msg(self, dataclass, ip_addr, port):
        """ отправляет входящий dataclass в обработчик"""
        try:
            # server routing
            if isinstance(dataclass, AuthenticateMessage):
                return self.server_msg_handler.authenticate_client(dataclass)
            elif isinstance(dataclass, OnChatMessage):
                return self.server_msg_handler.on_chat(dataclass)
            elif isinstance(dataclass, P2PMessage):
                return self.server_msg_handler.on_peer(dataclass)
            elif isinstance(dataclass, BaseClientMessage):
                if BaseClientMessage.action == 'quit':
                    return self.server_msg_handler.unregister(dataclass)
            else:
                return self.server_msg_handler.on_unhandled_msg(dataclass)

            # client routing

        except AttributeError:
            return self.server_msg_handler.on_unhandled_msg(dataclass, ip_addr, port)
