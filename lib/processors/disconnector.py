from datetime import datetime
import logging
import logs.config_server_log


class Disconnector:
    def __init__(self):
        self.logger = logging.getLogger('server_log')
        self.disconnect_flag = bool
        self.disconnect_response = {}

    @property
    def is_disconnected(self):
        return self.disconnect_flag

    @property
    def get_disconnect_response(self):
        return self.disconnect_response if self.is_disconnected else None

    def disconnect(self, ip_addr, port, error=None):
        """ возвращает ответ для отключения клиента """
        if error:
            self.logger.error('Client %s %s disconnected. Catch an error: %s', ip_addr, port, error)
        else:
            self.logger.error('Client %s %s disconnected without errors', ip_addr, port)
        self.disconnect_flag = True
        self.disconnect_response = {'response': 400,
                                    'time': str(datetime.now()),
                                    'error': f'<{ip_addr}:{port}>: wrong request or JSON-object'}
