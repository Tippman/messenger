import socket
from log.client_log_config import log_fn_info
from messenger.serializer import Serializer


class ClientSoket:
    def __init__(self, sock):
        self._s = sock

    @log_fn_info
    def send(self, msg):
        self._s.send(msg)

    @log_fn_info
    def recv(self, data_size=10000):
        return self._s.recv(data_size)
