import json


class Storage(object):
    storage = {}

    def __init__(self, users_config):
        self.storage = json.loads(users_config)

    def getName(self, id):
        if (
            ("names" in self.storage.keys())
            and (id in self.storage["names"].keys())
            and ("name" in self.storage["names"][id].keys())
        ):
            return self.storage["names"][id]["name"]

    def setName(self, id, name):
        if "names" not in self.storage.keys():
            self.storage["names"] = {}
        if id not in self.storage["names"].keys():
            self.storage["names"][id] = {}
        self.storage["names"][id]["name"] = name

    def getMembers(self):
        if "members" in self.storage.keys():
            return self.storage["members"]
        return []
