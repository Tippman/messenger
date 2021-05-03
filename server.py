"""Модуль управления сервером."""
import datetime
import sys
from queue import Queue

from PyQt5.QtWidgets import QApplication
from select import select
import socket
import threading

from sqlalchemy.orm import sessionmaker

from db.client_db import ClientStorage, ClientHistoryStorage
from lib.processors.message_dataclasses import SuccessServerMessage, ErrorClientMessage, P2PMessageReceive
from lib.processors.message_sender import MessageSender
from lib.variables import *
from lib.processors.receive_message_processor import MessageSplitter
from gui.server_gui import MainWindow


class Server:
    """Основной класс управления сервером."""

    def __init__(self, SERVER_ADDR):
        self.logger = logging.getLogger('server_log')
        self.SERVER_ADDR = SERVER_ADDR
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)
        self.clients = []
        self.nicknames = {}  #: dict with online clients = {'login': {'ip':ip, 'port':port}, ... }
        self.msg_splitter = MessageSplitter()
        self.message_sender = MessageSender()
        self.send_buffer = self.message_sender.send_buffer
        self.server_queue = Queue()

    def disconnect_socket(self, sock, login=None) -> None:
        """Отключает сокет. Удаляет инфо клиента из online словаря nicknames.

        :param sock: Сокет клиента, который необходимо отключить.
        :param login: Логин, который необходимо отключить. По умолчанию - None.
        :type sock: file
        :type login: str
        """
        # TODO как получить адрес клиента если он отключился?
        self.logger.info('Client disconnected')
        sock.close()
        if login:
            try:
                removable_addr = self.nicknames.pop(login)
            except KeyError:
                self.logger.info('Client %s already disconnected', login)
        if sock in self.clients:
            self.clients.remove(sock)

    def clients_read(self, r_sockets):
        """Читает данные из сокетов, от которых поступили запросы,
        скармливает их на обработку в :class:`lib.processors.receive_message_processor.MessageSplitter`
        и записывает ответы.

        :return: Возвращает словарь ответов клиентам, где ключ - сокет клиента, значение - ответ сервера.
        :rtype: dict
        :param r_sockets: Список сокетов, из которых получены данные.
        :type r_sockets: list[file]
        """
        responses = {}
        for sock in r_sockets:
            try:
                data = sock.recv(MAX_MSG_SIZE)  # читаем запакованные через struct данные

                # скармливаем данные с целью выполнить действия и сформировать ответ клиентам
                self.msg_splitter.feed(data=data, server_queue=self.server_queue)
                responses[sock] = self.send_buffer.data[0]
                self.send_buffer.bytes_sent()
            except IndexError:
                # если буфер отправки пуст - ничего не делаем
                pass
            except:
                # удаляем сокет из переченя если клиент отключился
                self.disconnect_socket(sock)
        return responses

    def clients_write(self, responses: dict, w_sockets: list) -> None:
        """Направляет ответы в сокеты, доступные для записи.

        :param responses: Словарь ответов сервера клиентам, сформированных в
        :param w_sockets: Список сокетов, доступных для получения ответов.
        """
        try:
            for sock in w_sockets:
                for author_sock, response in responses.items():
                    if author_sock == sock:
                        sock.send(response)
        except:
            # удаляем сокет из переченя если клиент отключился
            self.disconnect_socket(sock)

    @staticmethod
    def create_db_connection():
        """Создает соединение с БД.

        :return: Возвращает объект сессии.
        """
        Session = sessionmaker(bind=ENGINE)
        session = Session()
        return session

    def get_client_contacts(self, client_sock, addr: tuple) -> None:
        """Отправляет в *client_sock* action-запрос данных о получении списка контактов,
        скармливает упакованные даннные в :class:`lib.processors.receive_message_processor.MessageSplitter`,
        получает ответ и отправляет обратно клиенту.

        :param client_sock: Сокет клиента, от которого поступил запрос.
        :param addr: Кортеж из IP адреса и порта клиента, от которого поступил запрос.
        """
        self.logger.info('Getting client contact list %s', str(addr))

        client_sock.send('GET_CONTACTS'.encode(ENCODING_FORMAT))
        request_data = client_sock.recv(MAX_MSG_SIZE)

        self.msg_splitter.feed(request_data)
        client_sock.send(self.send_buffer.data[0])
        self.send_buffer.bytes_sent()

    def get_socket_by_address(self, ip_addr: str, port: int):
        """Возвращает сокет из списка подключенных клиентов. Если клиент оффлайн - возвращает None"""
        for sock in self.clients:
            sock_ip, sock_port = sock.getpeername()
            if sock_ip == ip_addr and sock_port == port:
                return sock
        return None

    def send_p2p_message(self, queue_item: dict) -> None:
        """Обработка и отправка сообщений p2p.
        Словарь с запросом получен из очереди сервера *server_queue_handler* .
        Ответы отправителям запросов направляются из данного метода.
        Словарь с запросом *queue_item* десериализуется, проверяется наличие адресата в online clients через
        словарь *Server.nicknames*. Если получатель online - ему напарвляется датакласс с сообщением отправителя.
        Ответ о статусе отправки сообщения возвращается инициатору отправки.

        :param queue_item: Словарь из обработчика очереди сервера.
        :return: None
        """
        author_login = queue_item['author_login']
        author_ip = str(queue_item['author_ip'])
        author_port = queue_item['author_port']
        target_login = queue_item['target_login']
        message = queue_item['message']

        if target_login in self.nicknames.keys():
            self.logger.info('sending p2p message from "%s" to online client "%s"',
                             author_login, target_login)
            target_ip, target_port = self.nicknames[target_login].values()
            target_sock = self.get_socket_by_address(target_ip, target_port)

            # Формируем и упаковываем датакласс для отправки получателю
            message_datacls_to_target = P2PMessageReceive(action='p2p_receive',
                                                          time=str(datetime.datetime.now()),
                                                          author=author_login,
                                                          message=message)
            self.message_sender.send(message_datacls_to_target)
            if self.send_buffer.data:
                message_data_to_target = self.send_buffer.data[0]
                self.send_buffer.bytes_sent()
                # Отправляем сообщение получателю
                target_sock.send(message_data_to_target)

            # Формируем ответ отправителю
            response_datacls = SuccessServerMessage(
                response=200,
                time=str(datetime.datetime.now()),
                alert=f'Message sent to client "{target_login}"')
        else:
            # Формируем ответ отправителю (получатель офлайн)
            self.logger.info('sending p2p message from "%s" to client "%s" failed. Target is offline.',
                             author_login, target_login)
            response_datacls = ErrorClientMessage(
                response=410,
                time=str(datetime.datetime.now()),
                error=f'Target client "{target_login}" is offline')

        author_sock = self.get_socket_by_address(author_ip, author_port)
        self.message_sender.send(response_datacls)
        if self.send_buffer.data:
            # Отправляем ответ автору сообщения
            response_data = self.send_buffer.data[0]
            self.send_buffer.bytes_sent()
            author_sock.send(response_data)

    def server_queue_handler(self, stopper) -> None:
        """Обработка очереди сервера (наполняется из :class:`lib.processors.message_handlers.ServerMessageHandler`).

        :param stopper: Остановщик потока сервера.
        """
        while not stopper.is_set():
            if not self.server_queue.empty():
                queue_item = self.server_queue.get_nowait()
                if isinstance(queue_item, dict):
                    try:

                        if queue_item['action'] == 'p2p':
                            self.send_p2p_message(queue_item)
                        elif queue_item['action'] == 'disconnect':
                            ip_addr = str(queue_item['ip_addr'])
                            port = queue_item['port']
                            for sock in self.clients:
                                sock_ip, sock_port = sock.getsockname()
                                if sock_ip == ip_addr and sock_port == port:
                                    sock.send(queue_item['action'].encode(ENCODING_FORMAT))
                        elif queue_item['action'] == 'success_auth':
                            client_login = queue_item['login']
                            ip_addr = str(queue_item['ip_addr'])
                            port = queue_item['port']
                            # Добавляем данные клиента в словарь актиынх подключений
                            self.nicknames[client_login] = {'ip': ip_addr, 'port': port}
                            for sock in self.clients:
                                sock_ip, sock_port = sock.getsockname()
                                if sock_ip == ip_addr and sock_port == port:
                                    self.get_client_contacts(sock, (ip_addr, port))
                                    self.logger.info('Success authorize client %s', client_login)
                    except KeyError as e:
                        self.logger.debug('Error while handling server queue. Key err: %s.', e)
                    except ValueError:
                        self.logger.debug('target is offline')
                    except Exception:
                        raise

    def run(self, event):
        """Основной поток обработки входящих соединений.

        :param event: Остановщик основного потока сервера.
        """
        print('Server is listening...')

        self.server.bind(self.SERVER_ADDR)
        self.server.listen(MAX_CONNECTIONS)
        self.server.settimeout(0.2)

        server_queue_thr = threading.Thread(target=self.server_queue_handler, args=(event,))
        server_queue_thr.start()

        while not event.is_set():
            try:
                client, addr = self.server.accept()
                print(f'Connected with {str(addr)}')
                ready = select([client], [], [], 1)
                if ready[0]:
                    self.logger.debug('server get a response from client after connect')
                    request_data = client.recv(MAX_MSG_SIZE)
                    self.msg_splitter.feed(data=request_data, server_queue=self.server_queue)
                    client.send(self.send_buffer.data[0])
                    self.send_buffer.bytes_sent()

                self.clients.append(client)

            except OSError:
                pass
            except KeyboardInterrupt:
                event.set()
            except Exception as e:
                # print(e)
                raise
            finally:
                r_sockets = []
                w_sockets = []
                try:
                    r_sockets, w_sockets, e = select(self.clients, self.clients, [], 0)
                except:
                    self.clients.remove(client)  # если клиент отключился
                responses = self.clients_read(r_sockets)
                if responses:
                    self.clients_write(responses, w_sockets)


if __name__ == "__main__":
    server = Server(SERVER_ADDR)
    server_kill = threading.Event()
    serv_thr = threading.Thread(target=server.run, args=(server_kill,))
    serv_thr.start()

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec_()

    server_kill.set()
    serv_thr.join()
