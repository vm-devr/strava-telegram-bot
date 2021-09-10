import json


class Storage(object):
    storage = {}

    def __init__(self, users_config):
        self.storage = json.loads(users_config)

    def get_name(self, id_):
        if (
            ("members" in self.storage.keys())
            and (id_ in self.storage["members"].keys())
            and ("name" in self.storage["members"][id_].keys())
        ):
            return self.storage["members"][id_]["name"]

        return ""

    def get_members(self):
        return [int(x) for x in self.storage["members"].keys()]
