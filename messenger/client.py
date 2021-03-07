from messenger.messages import Authentificate
from messenger.serializer import Serializer


class Client:
    def __init__(self, client_socket, account_name, serializer=Serializer()):
        self._client_socket = client_socket
        self._account_name = account_name
        self._serializer = serializer

    def authenticate(self, password):
        msg = Authentificate(self._account_name, password)
        data = self._serializer.serialize(msg)
        self._client_socket.send(data)

    def get_response(self):
        data = self._client_socket.recv()
        response_msg = self._serializer.deserialize(data)
        return response_msg