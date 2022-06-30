import json


class Config:
    def __init__(self, fn: str):
        self.fn = fn
        self.config = json.load(open(fn))

    def update(self, key, value):
        self.config[key] = value
        json.dump(self.config, open(self.fn, "w"))

    def get(self, key):
        return self.config[key]
