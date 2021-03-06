"""Модуль инициализации GUI сервера."""
import logging
from pathlib import Path

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from sqlalchemy.orm import sessionmaker

import logs.config_server_log
from db.client_db import ClientHistoryStorage, ClientStorage
from lib.variables import ENGINE


class MainWindow(QMainWindow):
    """Главное окно программы сервера."""

    def __init__(self):
        super().__init__()
        ui_file_path = Path(__file__).parent.parent.absolute() / "ui/server.ui"
        uic.loadUi(ui_file_path, self)

        self._logger = logging.getLogger('server_admin_app_log')
        self._logger.debug('Server application start')

        # управление БД и создание сессии
        self._Session = sessionmaker(bind=ENGINE)
        self._session = self._Session()
        self._client_storage = ClientStorage(self._session)
        self._client_history_storage = ClientHistoryStorage(self._session)

        # отрисовка начальных данных и установка обработчиков событий
        self.set_clients_tab_signals()
        self.set_clients_history_tab_signals()
        self.draw_clients_table()
        self.draw_clients_history_table()

        self.tabWidget.setCurrentIndex(0)  # установка начальной вкладки

    def set_clients_tab_signals(self):
        """Устанавливает обработчики на кнопки Clients Tab."""
        self._logger.debug('Setup clients tab events')
        self.clientListUpdateButton.clicked.connect(self.draw_clients_table)

    def set_clients_history_tab_signals(self):
        """Устанавливает обработчики на кнопки Clients History Tab."""
        self._logger.debug('Setup clients history tab events')
        self.clientHistoryUpdateButton.clicked.connect(self.draw_clients_history_table)

    def draw_clients_table(self):
        """Рендер таблицы с пользователями. отображает 2 колонки - id and login."""
        self._logger.debug('Drawing clients table')
        clients = self._client_storage.get_all_clients()
        if clients:
            self.clientListTableWidget.setRowCount(len(clients))
            for row_num, client in enumerate(clients):
                id_item = QTableWidgetItem(str(client.id))
                login_item = QTableWidgetItem(client.login)
                self.clientListTableWidget.setItem(row_num, 0, id_item)  # id col
                self.clientListTableWidget.setItem(row_num, 1, login_item)  # login col

    def draw_clients_history_table(self):
        """Рендер таблицы с историей пользователей.
        отображает все колонки в строке выборки БД (кроме служебной _sa_instance_state).
        """
        self._logger.debug('Drawing clients history table')

        client_histories = self._client_history_storage.gat_all_records()
        if client_histories:
            headers = [key for key in client_histories[0].__dict__.keys()
                       if key != '_sa_instance_state']
            self.clientHistoryTableWidget.setRowCount(len(client_histories))
            self.clientHistoryTableWidget.setColumnCount(len(headers))
            self.clientHistoryTableWidget.setHorizontalHeaderLabels(headers)

            for row_num, client_history in enumerate(client_histories):
                for col_num, key in enumerate(headers):
                    item = QTableWidgetItem(str(client_history.__dict__[key]))
                    self.clientHistoryTableWidget.setItem(row_num, col_num, item)
