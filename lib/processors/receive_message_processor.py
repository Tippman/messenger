import struct
import datetime
import json
import logging
import logs.config_server_log
from icecream import ic
from lib.variables import PACK_FORMAT, ENCODING_FORMAT
import ipaddress
from lib.processors.message_factories import MessageFactory
from lib.processors.disconnector import Disconnector


class Deserializer:
    """ Десериалайзер входящих заголовков и сообщений """
    def __init__(self,
                 loads=json.loads,
                 encoding=ENCODING_FORMAT,
                 msg_factory=MessageFactory(),
                 disconnector=Disconnector()):
        self._loads = loads
        self._encoding = encoding
        self._msg_factory = msg_factory
        self._disconnector = disconnector
        self._logger = logging.getLogger('server_log')

    def on_msg(self, ip_pack: bytes or None, port: int or None, msg_data: bytes):
        """ преобразует байты в словарь и отправляет его для сборки датакласса  """
        ip_addr = ipaddress.IPv4Address(ip_pack)
        try:
            msg_string = msg_data.decode(self._encoding)
            msg_dict = self._loads(msg_string)
            self._msg_factory.on_msg(msg_dict=msg_dict, ip_addr=ip_addr, port=port)
        except Exception as e:
            self._disconnector.disconnect(ip_addr, port, e)


class MessageSplitter:
    """ Класс начальной обработки входящих данных """
    def __init__(self,
                 pack_format=PACK_FORMAT,
                 deserializer=Deserializer()):
        self.pack_format = pack_format
        self.deserializer = deserializer
        self._logger = logging.getLogger('server_log')

    def feed(self, data):
        """ разбивает входящие данные на размер сообщения, ip клиента, port клиента и само сообщение """
        msg_len, ip_pack, port, data_body = struct.unpack(self.pack_format, data)
        data_body = data_body[:msg_len]
        self.deserializer.on_msg(ip_pack=ip_pack, port=port, msg_data=data_body)
