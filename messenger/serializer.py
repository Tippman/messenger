import json
import time
from messenger.messages import Authentificate, ServerResponse


class Serializer:
    def __init__(self, dumps=json.dumps, loads=json.loads, encoding='utf-8', get_time_fn=time.time):
        self._dumps = dumps
        self._loads = loads
        self._encoding = encoding
        self._get_time_fn = get_time_fn

    def serialize(self, msg):
        if isinstance(msg, Authentificate):
            result_dict = {
                "action": "authenticate",
                "time": self._get_time_fn(),
                "user": {
                    "account_name": msg.account_name,
                    "password": msg.password,
                }
            }
            result_str = self._dumps(result_dict)
            return result_str.encode(self._encoding)

        if isinstance(msg, ServerResponse):
            result_dict = {
                'response': msg.responce,
                'time': self._get_time_fn(),
                'alert': msg.alert,
            }
            result_str = self._dumps(result_dict)
            return result_str.encode(self._encoding)

    def deserialize(self, data):
        return self._loads(data)
