from lib.processors.message_dataclasses import *


class ServerMessageHandler:
    # обработка сообщений от клиента на сервере
    def __init__(self):
        pass

    def on_chat(self, dataclass):
        pass

    def register(self, dataclass):
        pass

    def unregister(self, dataclass):
        pass

    def on_peer(self, dataclass):
        pass

    def on_unhandled_msg(self, dataclass):
        pass


class ClientMessageHandler:
    # обработка сообщений от сервера на склиенте
    def status_200(self, dataclass):
        pass

    def status_400(self, dataclass):
        pass


class MessageRouter:
    """ Роутер сообщений. принимает dataclasses и направляет их в соответствующий обработчик ServerHandler или ClientHandler """

    def __init__(self,
                 server_msg_handler=ServerMessageHandler(),
                 client_msg_handler=ClientMessageHandler()):
        self.server_msg_handler = server_msg_handler
        self.client_msg_handler = client_msg_handler

    def on_msg(self, dataclass):
        """ отправляет входящий dataclass в обработчик"""
        try:
            # server routing
            if isinstance(dataclass, AuthenticateMessage):
                self.server_msg_handler.register(dataclass)
            elif isinstance(dataclass, OnChatMessage):
                self.server_msg_handler.on_chat(dataclass)
            elif isinstance(dataclass, P2PMessage):
                self.server_msg_handler.on_peer(dataclass)
            elif isinstance(dataclass, BaseClientMessage):
                if BaseClientMessage.action == 'quit':
                    self.server_msg_handler.unregister(dataclass)
            else:
                self.server_msg_handler.on_unhandled_msg(dataclass)

            # client routing

        except AttributeError:
            pass
