import json

from messenger.serializer import Serializer
from messenger.messages import Authentificate


def test_serialize_authenticate():
    msg = Authentificate('tippman', 'MyPassword')

    exepted_time = 123
    expected_msg = {
        "action": "authenticate",
        "time": exepted_time,
        "user": {
            "account_name": msg.account_name,
            "password": msg.password,
        }
    }
    expected_data = json.dumps(expected_msg).encode('utf-8')

    sut = Serializer(get_time_fn=lambda :exepted_time)
    assert sut.serialize(msg) == expected_data
