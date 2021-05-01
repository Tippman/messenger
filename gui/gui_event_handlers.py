import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class SuccessEvent(QtCore.QEvent):
    def __init__(self, response=None, alert=None):
        super().__init__(QtCore.QEvent.User)
        self.response = response
        self.alert = alert


class FailedAuthEvent(QtCore.QEvent):
    def __init__(self):
        super().__init__(QtCore.QEvent.User)


class FailedRegisterEvent(QtCore.QEvent):
    def __init__(self, error=None):
        super().__init__(QtCore.QEvent.User)
        self.error = error


class UiNotifier:
    def __init__(self, app, receiver=None, ):
        self.app = app
        self.receiver = receiver

    def notify_success(self, response=None, alert=None):
        self.app.postEvent(self.receiver, SuccessEvent(response=response, alert=alert))

    def notify_failed_auth(self):
        self.app.postEvent(self.receiver, FailedAuthEvent())

    def notify_failed_register(self, error=None):
        self.app.postEvent(self.receiver, FailedRegisterEvent(error=error))
