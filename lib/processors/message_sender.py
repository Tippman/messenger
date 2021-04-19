import ipaddress
import struct
from dataclasses import asdict
import json
from icecream import ic
from lib.variables import ENCODING_FORMAT, DEFAULT_IP, DEFAULT_PORT, PACK_FORMAT
import logging
import logs.config_server_log


class SendBuffer:
    def __init__(self):
        self._out = []

    def send(self, data):
        self._out.append(data)

    def bytes_sent(self):
        return self._out.pop(0)

    @property
    def data(self):
        return self._out


class Serializer:
    def __init__(self, encoding=ENCODING_FORMAT):
        self._encoding = encoding

    def pack_data(self, data, client_ip, client_port) -> bytes:
        """ упаковывает данные с заголовками:
            | msg len: 2b | client ip: 4b | client port: 2b | msg_dict: 1024 - 8b |
            возвращает bytes (struct) """
        msg_dict_pack = json.dumps(data).encode(ENCODING_FORMAT)
        package_data = struct.pack(PACK_FORMAT,
                                   len(msg_dict_pack),  # длина отправляемого сообщения (словаря с запросом)
                                   ipaddress.IPv4Address(client_ip).packed,
                                   client_port,
                                   msg_dict_pack)  # сам словарь с запросом
        return package_data

    # def on_msg(self, response_dict) -> None:
    #     """ сериализует словарь в json объект, кодирует и передает на отправку байты """
    #     json_dict = json.dumps(response_dict)
    #     data = json_dict.encode(self._encoding)
    #     self.send_buffer.send(data)


class MessageSender:
    def __init__(self, serializer=Serializer(), send_buffer=SendBuffer()):
        self._serializer = serializer
        self.send_buffer = send_buffer

    def send(self, dataclass) -> None:
        """ получает датасласс с ответом сервера, преобразует в словарь и отправляет на сборку в сериалайзер """
        response_dict = asdict(dataclass)
        data = self._serializer.pack_data(response_dict, DEFAULT_IP, DEFAULT_PORT)
        self.send_buffer.send(data)
