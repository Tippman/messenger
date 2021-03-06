import socket

from messenger.serializer import Serializer


class ClientSoket:
    def __init__(self, sock):
        self._s = sock

    def send(self, msg):
        self._s.send(Serializer().serialize(msg))

    def recv(self, data_size):
        self._s.recv(data_size)
