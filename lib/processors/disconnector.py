"""Модуль отключения клиента в случае ошибок в процессе обработки запросов."""
from datetime import datetime
import logging
import logs.config_server_log


class Disconnector:
    """Класс-дисконнектор"""

    def __init__(self):
        self.logger = logging.getLogger('server_log')
        self.disconnect_flag = bool
        self.disconnect_response = {}

    def disconnect(self, ip_addr, port, error=None, server_queue=None):
        """Наполняет очередь сервера запросами на отключение клиента."""
        if error:
            self.logger.error('Client %s %s disconnected. Catch an error: %s', ip_addr, port, error)
        else:
            self.logger.error('Client %s %s disconnected without errors', ip_addr, port)
        self.disconnect_flag = True
        self.disconnect_response = {'response': 400,
                                    'time': str(datetime.now()),
                                    'error': f'<{ip_addr}:{port}>: wrong request or JSON-object'}
        server_queue.put({'action': 'disconnect',
                          'ip_addr': ip_addr,
                          'port': port, })
