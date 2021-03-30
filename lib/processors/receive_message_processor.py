import struct
import datetime
import json

from lib.variables import PACK_FORMAT, ENCODING_FORMAT

from lib.processors.message_factories import MessageFactory


class Deserializer:
    def __init__(self,
                 loads=json.loads,
                 encoding=ENCODING_FORMAT,
                 msg_factory=MessageFactory()):
        self._loads = loads
        self._encoding = encoding
        self._msg_factory = msg_factory

    def on_msg(self, msg_size: int, msg_body: bytes):
        """ преобразует байты в словарь и отправляет его для сборки датакласса  """
        try:
            msg_string = msg_body.decode(self._encoding)
            msg_dict = self._loads(msg_string)
            self._msg_factory.on_msg(dict=msg_dict, msg_size=msg_size)
        except:
            print('disconnect')
            self.disconnect()

    def disconnect(self):
        pass


class MessageSplitter:
    def __init__(self,
                 pack_format=PACK_FORMAT,
                 deserializer=Deserializer()):
        self.pack_format = pack_format
        self.deserializer = deserializer

    def feed(self, data):
        """ разбивает входящие данные размер сообщения и само сообщение """
        data_header, data_body = struct.unpack(self.pack_format, data)
        data_body = data_body[:data_header]
        self.deserializer.on_msg(msg_size=data_header, msg_body=data_body)


strr = 'aвыпа fds1234'
msg_d = {
    "action": "on chat",
    "time": str(datetime.datetime.now()),
    "to": "account_name",
    "author": "account_name",
    "message": strr
}

# msg = str(msg_d)

msg = json.dumps(msg_d)

# msg = MsgDict(**msg_d)
# print(msg)
# print(msg.action)
#
msg_bytes = msg.encode(ENCODING_FORMAT)

package = struct.pack(PACK_FORMAT, len(msg_bytes), msg_bytes)

ms = MessageSplitter()
ms.feed(package)
