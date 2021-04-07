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
            return self._msg_factory.on_msg(msg_dict=msg_dict, ip_addr=ip_addr, port=port)
        except Exception as e:
            return self._disconnector.disconnect(ip_addr, port, e)


class MessageSplitter:
    def __init__(self,
                 pack_format=PACK_FORMAT,
                 deserializer=Deserializer()):
        self.pack_format = pack_format
        self.deserializer = deserializer

    def feed(self, data):
        """ разбивает входящие данные на размер сообщения, ip слиента, port клиента и само сообщение """
        msg_len, ip_pack, port, data_body = struct.unpack(self.pack_format, data)
        data_body = data_body[:msg_len]
        return self.deserializer.on_msg(ip_pack=ip_pack, port=port, msg_data=data_body)



# strr = 'aвыпа fds1234'
# msg_d = {
#     "action": "on chat",
#     "time": str(datetime.datetime.now()),
#     "to": "account_name",
#     "author": "account_name",
#     "message": strr
# }
#
# msg = json.dumps(msg_d)
#
# msg_bytes = msg.encode(ENCODING_FORMAT)
#
# package = struct.pack(PACK_FORMAT, len(msg_bytes), msg_bytes)
#
# ms = MessageSplitter()
# ms.feed(package)
