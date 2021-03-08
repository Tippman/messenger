from unittest.mock import MagicMock

from messenger.client import Client
from messenger.messages import Authentificate


def test_authenticate():
    mock_sock = MagicMock()
    mock_serializer = MagicMock()
    sut = Client(mock_sock, 'username', mock_serializer)

    mock_serializer.serialize.return_value = b'1232Test'

    sut.authenticate('password')

    mock_serializer.serialize.assert_called_once_with(Authentificate('username', 'password'))
    mock_sock.send.assert_called_once_with(b'1232Test')
    # assert mock_serializer.msg == Authentificate('username', 'password')
    # assert mock_sock.msg == b'1232Test'
