import logging

# Быстрая настройка логгирования может быть выполнена так:
# logging.basicConfig(filename="gui.log",
#     format="%(levelname)-10s %(asctime)s %(message)s",
#     level = logging.INFO
# )

# Можно выполнить более расширенную настройку логгирования.
# Создаём объект-логгер с именем db_admin_gui:
logger = logging.getLogger('messenger.server')

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
fh = logging.FileHandler("messenger.server.log", encoding='utf-8')
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



if __name__ == '__main__':
    # Создаём потоковый обработчик логгирования (по умолчанию sys.stderr):
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    # В логгирование передаем имя текущей функции и имя вызвавшей функции
    logger.info('Тестовый запуск логгирования')
