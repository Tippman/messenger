"""Модуль управления виджетом логин-окна чата."""
import logging
import time

from icecream import ic

from lib.variables import ENCODING_FORMAT
from logs import config_server_log
import threading
from queue import Queue

from gui.gui_event_handlers import SuccessEvent, FailedAuthEvent, FailedRegisterEvent
from lib.processors.client_message_factory.client_message_factory import ClientMessageFactory
from pathlib import Path

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget


class MainLoginWindow(QWidget):
    """Класс-окно авторизациии клиента."""

    def __init__(self, client):
        super().__init__()
        ui_file_path = Path(__file__).parent.parent.absolute() / "ui/client_login.ui"
        uic.loadUi(ui_file_path, self)

        self.client = client

        self.logger = logging.getLogger('client_login_app_log')
        self.logger.debug('Client-login application start')

        # установка обработчиков сигналов
        self.set_login_widget_signals()

        # скрываем поля для регистрации
        self.repeatPasswordLineEdit.hide()
        self.submitRegisterPushButton.hide()
        self.repeatPasswordLabel.hide()
        self.cancelRegistrationPushButton.hide()

    def event(self, e: QtCore.QEvent) -> bool:
        """Обработка событий авторизации."""
        if e.type() == QtCore.QEvent.User:
            if isinstance(e, SuccessEvent):
                self.logger.debug('catch success msg')
                if e.response == 201:
                    self.logger.info('New account created!')
                    self.errorArea.setText('New account created!')
                    self.hide_register_fields()
                elif e.response == 200:
                    self.logger.info('Success authorize!')
                    self.errorArea.setText('Success authorize!')
                    time.sleep(1)
                    self.close()
            elif isinstance(e, FailedAuthEvent):
                self.logger.debug('catch failed auth')
                self.errorArea.setText('Wrong login or password!')
                self.client.disconnect()
            elif isinstance(e, FailedRegisterEvent):
                self.logger.debug('Register failed!')
                self.errorArea.setText(e.error)
                self.client.disconnect()

        return super().event(e)

    def set_login_widget_signals(self):
        """Установка сигналов логин-виджета."""
        self.connectButton.clicked.connect(self.connect_to_server)
        self.registerPushButton.clicked.connect(self.show_register_fields)
        self.cancelRegistrationPushButton.clicked.connect(self.hide_register_fields)
        self.submitRegisterPushButton.clicked.connect(self.submit_register)

    def submit_register(self):
        """Отправка формы регистрации и проверка паролей."""
        self.logger.debug('connecting to server, register')
        server_ip = self.addressLineEdit.text()
        server_port = self.portSpinBox.value()
        self.client.SERVER_ADDR = (server_ip, server_port)

        login = self.loginLineEdit.text()
        password_1 = self.passwordLineEdit.text()
        password_2 = self.repeatPasswordLineEdit.text()
        if password_1 == password_2:
            self.errorArea.setText('')
            self.client.login = login
            self.client.password = password_1
            self.client.client_thr_killer = threading.Event()
            self.client.run()
            self.client.client_queue.put({'action': 'add_new_client', 'login': login, 'password': password_1})
        else:
            self.errorArea.setText('Enter the same passwords!')

    def show_register_fields(self):
        """Открывает поля и кнопки для регистрации."""
        self.errorArea.setText('')
        self.repeatPasswordLineEdit.show()
        self.repeatPasswordLabel.show()
        self.cancelRegistrationPushButton.show()
        self.submitRegisterPushButton.show()
        self.registerPushButton.hide()
        self.connectButton.hide()

    def hide_register_fields(self):
        """Скрывает поля и кнопки для регистрации."""
        self.errorArea.setText('')
        self.repeatPasswordLineEdit.hide()
        self.repeatPasswordLabel.hide()
        self.cancelRegistrationPushButton.hide()
        self.submitRegisterPushButton.hide()
        self.registerPushButton.show()
        self.connectButton.show()

    def connect_to_server(self):
        """Устанавливает соедиение для зарегистрированных пользователей."""
        self.logger.debug('connecting to server')
        self.errorArea.setText('')
        server_ip = self.addressLineEdit.text()
        server_port = self.portSpinBox.value()
        self.client.SERVER_ADDR = (server_ip, server_port)
        self.client.login = self.loginLineEdit.text()
        self.client.password = self.passwordLineEdit.text()

        self.client.client_thr_killer = threading.Event()
        self.client.run()
        self.client.client_queue.put({'action': 'authenticate'})
