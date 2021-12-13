from dataclasses import dataclass
from typing import List


@dataclass
class Member:
    id_: int
    name: str

    def __lt__(self, other) -> bool:
        return self.name.lower() < other.name.lower()

    def __str__(self):
        return f'<a href="https://www.strava.com/athletes/{str(self.id_)}">{self.name}</a>'


class MemberList:
    @staticmethod
    def get_table(member_ids: List[Member]) -> List[str]:
        # The logo is needed for Telegram's preview. Because if it's not provided Telegram generates preview from
        # the picture of the first member.
        title = ['Бігуни <a href="https://gutsulrunning.club/images/2021/08/05/header_large.jpeg">GRC:</a>']
        body = [f"{i:2d}. {m}" for m, i in zip(sorted(member_ids), range(1, 1 + len(member_ids)))]
        return title + body
