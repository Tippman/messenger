from dataclasses import dataclass


@dataclass()
class Authentificate:
    account_name: str
    password: str


@dataclass()
class ServerResponse:
    responce: int
    alert: str
