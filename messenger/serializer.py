import json
import time
from messenger.messages import Authentificate


class Serializer:
    def __init__(self, dumps=json.dumps, encoding='utf-8', get_time_fn=time.time):
        self._dumps = dumps
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