"""Модуль управления уведомителем GUI клиента."""
import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class SuccessEvent(QtCore.QEvent):
    """Класс-уведомление об успешном событии."""
    def __init__(self, response=None, alert=None):
        super().__init__(QtCore.QEvent.User)
        self.response = response
        self.alert = alert


class FailedAuthEvent(QtCore.QEvent):
    """Класс-уведомление о неудачной попытке авторизации."""
    def __init__(self):
        super().__init__(QtCore.QEvent.User)


class FailedRegisterEvent(QtCore.QEvent):
    """Класс-уведомление о неудачной попытке регистрации."""
    def __init__(self, error=None):
        super().__init__(QtCore.QEvent.User)
        self.error = error


class FailedSendingMessage(QtCore.QEvent):
    """Класс-уведомление о неудачной попытке отправки сообщения."""
    def __init__(self, datacls):
        super().__init__(QtCore.QEvent.User)
        self.response = datacls.response
        self.time = datacls.time
        self.error = datacls.error


class InboxMessage(QtCore.QEvent):
    """Класс-уведомление о получении нового сообщения."""
    def __init__(self, message_datacls):
        super().__init__(QtCore.QEvent.User)
        self.author = message_datacls.author
        self.time = message_datacls.time
        self.message = message_datacls.message


class UiNotifier:
    """Класс-роутер удедомлений GUI."""
    def __init__(self, app, receiver=None, ):
        self.app = app
        self.receiver = receiver

    def notify_success(self, response=None, alert=None):
        """Уведомляет GUI об успешном ответе сервера."""
        self.app.postEvent(self.receiver, SuccessEvent(response=response, alert=alert))

    def notify_failed_auth(self):
        """Уведомляет GUI о неудачной попытке авторизации."""
        self.app.postEvent(self.receiver, FailedAuthEvent())

    def notify_failed_register(self, error=None):
        """Уведомляет GUI о неудачной попытке регистрации."""
        self.app.postEvent(self.receiver, FailedRegisterEvent(error=error))

    def notify_inbox_message(self, message_datacls):
        """Уведомляет GUI о входящем сообщении."""
        self.app.postEvent(self.receiver, InboxMessage(message_datacls))

    def notify_sending_failed(self, datacls):
        """Уведомляет GUI о неудачной попытке отправки сообщения."""
        self.app.postEvent(self.receiver, FailedSendingMessage(datacls))
