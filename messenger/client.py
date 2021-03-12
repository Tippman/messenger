from messenger.messages import Authentificate
from messenger.serializer import Serializer
import logging
import log.client_log_config


class Client:
    def __init__(self, client_socket, account_name, serializer=Serializer()):
        self._client_socket = client_socket
        self._account_name = account_name
        self._serializer = serializer
        self.log = logging.getLogger('messenger.client')

    def authenticate(self, password):
        msg = Authentificate(self._account_name, password)
        data = self._serializer.serialize(msg)
        self._client_socket.send(data)
        self.log.info('auth request from user')

    def get_response(self):
        data = self._client_socket.recv()
        response_msg = self._serializer.deserialize(data)
        self.log.info('response code %d', response_msg['response'])
        return response_msg
#init