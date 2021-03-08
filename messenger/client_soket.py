import socket

from messenger.serializer import Serializer


class ClientSoket:
    def __init__(self, sock):
        self._s = sock

    def send(self, msg):
        self._s.send(msg)

    def recv(self, data_size=10000):
        return self._s.recv(data_size)
