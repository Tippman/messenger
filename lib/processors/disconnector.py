from datetime import datetime
import logging
import logs.config_server_log


class Disconnector:
    def __init__(self):
        self.logger = logging.getLogger('server_log')

    def disconnect(self, ip_addr, port, error=None):
        """ возвращает ответ для отключения клиента """
        if error:
            self.logger.error('Client %s %s disconnected. Catch an error: %s', ip_addr, port, error)
        else:
            self.logger.error('Client %s %s disconnected without errors', ip_addr, port)

        response = {
            'response': 400,
            'time': str(datetime.now()),
            'error': f'<{ip_addr}:{port}>: wrong request or JSON-object'
        }
        return response
