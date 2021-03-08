import json
import unittest
import time
from messenger.serializer import Serializer
from messenger.messages import Authentificate, ServerResponse


class TestSerializer(unittest.TestCase):
    def setUp(self) -> None:
        self.exepted_time = time.time()
        self.sut = Serializer(get_time_fn=lambda: self.exepted_time)

    def test_serialize_authenticate(self):
        msg = Authentificate('tippman', 'qwerty12')

        expected_msg = {
            "action": "authenticate",
            "time": self.exepted_time,
            "user": {
                "account_name": msg.account_name,
                "password": msg.password,
            }
        }
        expected_data = json.dumps(expected_msg).encode('utf-8')

        assert self.sut.serialize(msg) == expected_data

    def test_serialize_access_authenticate_on_server(self):
        msg = ServerResponse(responce=200, alert='Success connection established!')
        expected_msg = {
            'response': 200,
            'time': self.exepted_time,
            'alert': 'Success connection established!'
        }
        expected_data = json.dumps(expected_msg).encode('utf-8')
        assert self.sut.serialize(msg) == expected_data

    def test_serialize_recieve_responce_on_authenticate(self):
        expected_msg = {
            'response': 200,
            'time': self.exepted_time,
            'alert': 'Success connection established!'
        }
        recieve_data = json.dumps(expected_msg).encode('utf-8')

        assert self.sut.deserialize(recieve_data) == expected_msg
