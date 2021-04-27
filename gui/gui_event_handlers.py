import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class SuccessEvent(QtCore.QEvent):
    def __init__(self, alert=None):
        super().__init__(QtCore.QEvent.User)
        self.alert = alert


class FailedAuthEvent(QtCore.QEvent):
    def __init__(self):
        super().__init__(QtCore.QEvent.User)


class UiNotifier:
    def __init__(self, app, receiver=None, ):
        self.app = app
        self.receiver = receiver

    def notify_success(self, alert=None):
        self.app.postEvent(self.receiver, SuccessEvent(alert=alert))

    def notify_failed_auth(self):
        self.app.postEvent(self.receiver, FailedAuthEvent())
