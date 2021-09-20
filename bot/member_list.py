from dataclasses import dataclass
from typing import List


@dataclass
class Member(object):
    id_: int
    name: str

    def __lt__(self, other) -> bool:
        return self.name.lower() < other.name.lower()


class MemberList(object):
    @staticmethod
    def printable(member_ids: List[Member]) -> List[str]:
        title = ['Бігуни <a href="https://gutsulrunning.club/images/2021/08/05/header_large.jpeg">GRC:</a>']
        body = [
            f'{i:2d}. <a href="https://www.strava.com/athletes/{str(m.id_)}">{m.name}</a>'
            for m, i in zip(sorted(member_ids), range(1, 1 + len(member_ids)))
        ]
        return title + body
