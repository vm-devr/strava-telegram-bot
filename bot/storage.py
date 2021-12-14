from typing import List


class Storage(object):
    storage = {}

    def __init__(self, users_config: str) -> None:
        for id_name in users_config.split(";"):
            if id_name := id_name.strip():
                spl = id_name.split(":", 1)
                id_, name = int(spl[0]), spl[1].strip()
                self.storage[id_] = name

    def get_name(self, id_: int) -> str:
        return self.storage.get(id_, "")

    def get_members(self) -> List[int]:
        return [x for x in self.storage.keys()]
