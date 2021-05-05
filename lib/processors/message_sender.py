"""Модуль сериализации и подготовки к отправке сообщений."""
import ipaddress
import json
import logging
import struct
from dataclasses import asdict

import logs.config_server_log
from lib.variables import (DEFAULT_IP, DEFAULT_PORT, ENCODING_FORMAT,
                           PACK_FORMAT)


class SendBuffer:
    """Класс-очередь отправки сообщений."""

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
    """Класс сериалайзер данных."""

    def __init__(self, encoding=ENCODING_FORMAT):
        self._encoding = encoding

    def pack_data(self, data, client_ip, client_port) -> bytes:
        """Упаковывает данные с заголовками:
        | msg len: 2b | client ip: 4b | client port: 2b | msg_dict: 1024 - 8b |
        возвращает bytes (struct).

        :param data: Данные для сериализации. Может быть любой python-объект.
        :param client_ip: IPv4Address клиента.
        :param client_port: Порт клиента.
        """
        msg_dict_pack = json.dumps(data).encode(ENCODING_FORMAT)
        package_data = struct.pack(PACK_FORMAT,
                                   len(msg_dict_pack),  # длина отправляемого сообщения (словаря с запросом)
                                   ipaddress.IPv4Address(client_ip).packed,
                                   client_port,
                                   msg_dict_pack)  # сам словарь с запросом
        return package_data


class MessageSender:
    """Класс, инициатор сериализации и отправки сообщений."""

    def __init__(self, serializer=Serializer(), send_buffer=SendBuffer()):
        self._serializer = serializer
        self.send_buffer = send_buffer

    def send(self, dataclass) -> None:
        """Получает датасласс с ответом сервера, преобразует в словарь и отправляет на сборку в сериалайзер.
        В результате выполнения функции данные можно получить из :class:`lib.processors.message_sender.SendBuffer`.
        """
        response_dict = asdict(dataclass)
        data = self._serializer.pack_data(response_dict, DEFAULT_IP, DEFAULT_PORT)
        self.send_buffer.send(data)
