import logging
import time

from icecream import ic

from logs import config_server_log
import threading
from queue import Queue

from gui.gui_event_handlers import SuccessEvent, FailedAuthEvent
from lib.processors.client_message_factory.client_message_factory import ClientMessageFactory
from pathlib import Path

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget


class MainLoginWindow(QWidget):
    """ класс-окно авторизациии клиента """

    def __init__(self, client):
        super().__init__()
        ui_file_path = Path(__file__).parent.parent.absolute() / "ui/client_login.ui"
        uic.loadUi(ui_file_path, self)

        self.client = client

        self.logger = logging.getLogger('client_login_app_log')
        self.logger.debug('Client-login application start')

        # установка обработчиков сигналов
        self.set_login_widget_signals()

    def event(self, e: QtCore.QEvent) -> bool:
        """ обработка событий авторизации """
        if e.type() == QtCore.QEvent.User:
            if isinstance(e, SuccessEvent):
                self.logger.debug('catch success auth')
                time.sleep(1)
                self.close()
            elif isinstance(e, FailedAuthEvent):
                self.logger.debug('catch failed auth')
                self.errorArea.setText('Wrong login or password!')
                self.client.disconnect()
        return super().event(e)

    def set_login_widget_signals(self):
        """ установка сигналов логин-виджета"""
        self.connectButton.clicked.connect(self.connect_to_server)

    def connect_to_server(self):
        self.logger.debug('connecting to server')
        server_ip = self.addressLineEdit.text()
        server_port = self.portSpinBox.value()
        self.client.SERVER_ADDR = (server_ip, server_port)
        self.client.login = self.loginLineEdit.text()
        self.client.password = self.passwordLineEdit.text()

        self.client.run()
