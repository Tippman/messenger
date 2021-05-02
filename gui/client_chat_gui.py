import logging

from PyQt5.QtCore import pyqtSignal
from icecream import ic
from sqlalchemy.orm import sessionmaker

from db.client_db import ClientStorage
from lib.variables import ENGINE
from logs import config_server_log
import time

from gui.gui_event_handlers import SuccessEvent, FailedAuthEvent, InboxMessage, FailedSendingMessage
from pathlib import Path

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget


class MainChatWindow(QMainWindow):
    """ класс-окно чата клиента """
    get_contacts_signal = pyqtSignal(tuple)

    def __init__(self, client):
        super().__init__()
        ui_file_path = Path(__file__).parent.parent.absolute() / "ui/client_main_window.ui"
        uic.loadUi(ui_file_path, self)

        self.client = client

        # управление БД и создание сессии
        self._Session = sessionmaker(bind=ENGINE)
        self._session = self._Session()
        self._client_storage = ClientStorage(self._session)

        self.chat_logger = logging.getLogger('client_chat_app_log')
        self.chat_logger.debug('Client-chat application start')

        # установка обработчиков сигналов
        self.set_chat_widget_signals()

        self.render_contact_list()

    def render_contact_list(self):
        """ загрузка списка контактов пользователя """
        client_contacts = self._client_storage.get_client_contacts(self.client.login)
        self.contactsListWidget.addItems(client_contacts)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == QtCore.QEvent.User:
            if isinstance(e, SuccessEvent):
                self.chat_logger.debug('catch success event')
            elif isinstance(e, InboxMessage):
                self.chat_logger.info('Catch inbox msg from %s', e.author)
                self.chatHistoryList.addItem(f'{e.author}: {e.message}')
            elif isinstance(e, FailedSendingMessage):
                self.chat_logger.info('Error while sending message: %s', e.error)
                self.chatHistoryList.addItem(e.error)
        return super().event(e)

    def set_chat_widget_signals(self):
        self.sendButton.clicked.connect(self.submit)

    def submit(self):
        target = self.contactsListWidget.currentItem().text()
        msg = self.messageLineEdit.text()
        self.chatHistoryList.addItem(f'{target}: {msg}')
        self.messageLineEdit.setText('')

        self.client.client_queue.put({'action': 'p2p', 'target': target, 'msg': msg})
