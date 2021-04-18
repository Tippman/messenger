import logging
from logs import config_server_log
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class MainLoginWindow(QMainWindow):
    """ класс-окно авторизациии клиента """

    def __init__(self):
        super().__init__()
        ui_file_path = Path(__file__).parent.parent.absolute() / "ui/client_login.ui"
        uic.loadUi(ui_file_path, self)

        self._logger = logging.getLogger('client_login_app_log')
        self._logger.debug('Client-login application start')
