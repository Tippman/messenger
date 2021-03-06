import pytest
from messenger.client_soket import ClientSoket


def test_init():
    sock = object()
    sut = ClientSoket(sock)
    assert sut._s == sock


