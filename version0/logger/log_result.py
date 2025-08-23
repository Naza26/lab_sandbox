import json


class LogResult:
    def __init__(self, filepath):
        self._filepath = filepath

    def as_json(self):
        with open(self._filepath, "r") as file:
            return json.load(file)
