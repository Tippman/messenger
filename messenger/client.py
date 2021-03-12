from messenger.messages import Authentificate
from messenger.serializer import Serializer
import logging
from log.client_log_config import log_fn_info


class Client:
    def __init__(self, client_socket, account_name, serializer=Serializer(), log=logging.getLogger('messenger.client')):
        self._client_socket = client_socket
        self._account_name = account_name
        self._serializer = serializer
        self._log = log

    @log_fn_info
    def authenticate(self, password):
        msg = Authentificate(self._account_name, password)
        data = self._serializer.serialize(msg)
        self._client_socket.send(data)
        self._log.info('auth request from user %s', self._account_name)

    @log_fn_info
    def get_response(self):
        data = self._client_socket.recv()
        response_msg = self._serializer.deserialize(data)
        self._log.info('response code %d', response_msg['response'])
        return response_msg
