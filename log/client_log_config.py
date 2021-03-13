import inspect
import logging
import sys
from functools import wraps

# Быстрая настройка логгирования может быть выполнена так:
# logging.basicConfig(filename="gui.log",
#     format="%(levelname)-10s %(asctime)s %(message)s",
#     level = logging.INFO
# )

# Можно выполнить более расширенную настройку логгирования.
# Создаём объект-логгер с именем db_admin_gui:
logger = logging.getLogger('messenger.client')

# Создаём объект форматирования:
formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s ")

# Возможные настройки для форматирования:
# -----------------------------------------------------------------------------
# | Формат         | Описание
# -----------------------------------------------------------------------------
# | %(name)s       | Имя регистратора.
# | %(levelno)s    | Числовой уровень важности.
# | %(levelname)s  | Символическое имя уровня важности.
# | %(pathname)s   | Путь к исходному файлу, откуда была выполнена запись в журнал.
# | %(filename)s   | Имя исходного файла, откуда была выполнена запись в журнал.
# | %(funcName)s   | Имя функции, выполнившей запись в журнал.
# | %(module)s     | Имя модуля, откуда была выполнена запись в журнал.
# | %(lineno)d     | Номер строки, откуда была выполнена запись в журнал.
# | %(created)f    | Время, когда была выполнена запись в журнал. Значением
# |                | должно быть число, такое как возвращаемое функцией time.time().
# | %(asctime)s    | Время в формате ASCII, когда была выполнена запись в журнал.
# | %(msecs)s      | Миллисекунда, когда была выполнена запись в журнал.
# | %(thread)d     | Числовой идентификатор потока выполнения.
# | %(threadName)s | Имя потока выполнения.
# | %(process)d    | Числовой идентификатор процесса.
# | %(message)s    | Текст журналируемого сообщения (определяется пользователем).
# -----------------------------------------------------------------------------

# Создаём файловый обработчик логгирования (можно задать кодировку):
fh = logging.FileHandler("messenger.client.log", encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

# Добавляем в логгер новый обработчик событий и устанавливаем уровень логгирования
logger.addHandler(fh)
logger.setLevel(logging.INFO)

# Возможные уровни логгирования:
# -----------------------------------------------------------------------------
# | Уровень важности | Использование
# -----------------------------------------------------------------------------
# | CRITICAL         | log.critical(fmt [, *args [, exc_info [, extra]]])
# | ERROR            | log.error(fmt [, *args [, exc_info [, extra]]])
# | WARNING          | log.warning(fmt [, *args [, exc_info [, extra]]])
# | INFO             | log.info(fmt [, *args [, exc_info [, extra]]])
# | DEBUG            | log.debug(fmt [, *args [, exc_info [, extra]]])
# -----------------------------------------------------------------------------

# Создаём потоковый обработчик логгирования (по умолчанию sys.stderr):
logger_func_call = logging.getLogger('messenger.function_call_info')
log_fn_formatter = logging.Formatter("%(asctime)s %(message)s")
f_handler = logging.FileHandler('messenger.func_calls.log', encoding='utf-8')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(log_fn_formatter)
logger_func_call.addHandler(f_handler)
logger_func_call.setLevel(logging.DEBUG)


def log_fn_info(func):
    """Выводит в файл информацию о вызываемой функции, переданных в нее аргументах,
    а также имя функции, инициирующей вызов текущей"""

    @wraps(func)
    def call(*args, **kwargs):
        insp_stack = inspect.stack()  # получаем стек вызовов вызываемой функции
        func_call_attrs = inspect.getcallargs(func, *args, **kwargs)  # получаем переданные в функцию параметры
        logger_func_call.info(
            f'Функция {func.__name__} была вызвана с параметрами {func_call_attrs} из функции {insp_stack[1].function}')
        return func(*args, **kwargs)

    return call
