"""Декораторы"""

import sys
import logging
import inspect
from functools import wraps

import logs.config_server_log
import logs.config_client_log

if sys.argv[0].rfind('server') > 0:
    # имя скрипта содержит server, значит это сервер
    DEC_LOGGER = logging.getLogger('server')
else:
    # =-1, не найдено, значит клент
    DEC_LOGGER = logging.getLogger('client')


def log(called_func):
    """Функция-декоратор. Выводит в файл информацию о вызываемой функции, переданных в нее аргументах,
    а также имя функции, инициирующей вызов текущей"""

    @wraps
    def log_saver(*args, **kwargs):
        insp_stack = inspect.stack()  # получаем стек вызовов вызываемой функции
        func_call_attrs = inspect.getcallargs(called_func, *args, **kwargs)  # получаем переданные в функцию параметры
        DEC_LOGGER.debug(
            f'Функция {called_func.__name__} была вызвана с параметрами {func_call_attrs} из функции {insp_stack[1].function}')
        ret_log_saver = called_func(*args, **kwargs)
        return ret_log_saver

    return log_saver
