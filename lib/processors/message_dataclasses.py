from dataclasses import dataclass
from datetime import datetime


# сообщения отправляемые клиентом
# “action”: “presence” — присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online;
# “action”: “prоbe” — проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online;
# “action”: “msg” — простое сообщение пользователю или в чат;
# “action”: “quit” — отключение от сервера;
# “action”: “authenticate” — авторизация на сервере;
# “action”: “join” — присоединиться к чату;
# “action”: “leave” — покинуть чат.
@dataclass()
class BaseClientMessage:
    action: str
    time: datetime
    author: str
    msg_size: int


@dataclass()
class OnChatMessage(BaseClientMessage):
    message: str


@dataclass()
class P2PMessage(BaseClientMessage):
    to: str
    message: str


@dataclass()
class AuthenticateMessage(BaseClientMessage):
    account_name: str
    password: str


# ответы/запросы сервера
@dataclass()
class BaseServerMessage:
    response: int
    time: datetime


@dataclass()
class InfoServerMessage(BaseServerMessage):
    # информационные сообщения:
    # 100 — базовое уведомление;
    # 101 — важное уведомление.
    alert: str


@dataclass()
class SuccessServerMessage(BaseServerMessage):
    # успешное завершение
    # 200 — OK
    # 201(created) — объект создан
    # 202(accepted) — подтверждение
    alert: str


@dataclass()
class ErrorClientMessage(BaseServerMessage):
    # ошибка на стороне клиента
    # 400 — неправильный запрос / JSON - объект
    # 401 — не авторизован
    # 402 — неправильный логин / пароль
    # 403(forbidden) — пользователь заблокирован
    # 404(not found) — пользователь / чат отсутствует на сервере
    # 409(conflict) — уже имеется подключение с указанным логином
    # 410(gone) — адресат существует, но недоступен(offline)
    error: str


@dataclass()
class ErrorServerMessage(BaseServerMessage):
    # ошибки сервера
    # 500
    error: str


@dataclass()
class PingClientMessage(BaseServerMessage):
    action: str  # 'probe'
