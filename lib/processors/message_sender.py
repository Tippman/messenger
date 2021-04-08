from dataclasses import asdict


class MessageSender:
    def __init__(self):
        pass

    def send(self, dataclass):
        """ получает датасласс с ответом сервера, преобразует в словарь и отправляет на сборку в сериалайзер """
        response_dict = asdict(dataclass)