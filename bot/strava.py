import json
import re
from typing import List

import requests
from leaderboard import LeaderBoard
from logger import log
from member_list import Member, MemberList
from storage import Storage


class Strava(LeaderBoard):
    session = requests.Session()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"

    def __init__(self, storage: Storage, group: int):
        self.storage = storage
        self.group = group

    def get_leaderboard(self, prev_week, elements):
        log.info("Reading latest leaderboard")

        def provide_name(ath):
            ath["name"] = self.get_name(ath["id"])
            return ath

        if elements > 99:
            elements = 99
        members = self.storage.get_members()
        raw_board = self._get_leaderboard(self.group, prev_week)
        filtered_board = list(filter(lambda ath: ath["id"] in members, raw_board))
        board = list(map(provide_name, filtered_board[:elements]))

        return self.printable(board)

    def get_name(self, id_: int) -> str:
        return self.storage.get_name(id_)

    def _get_leaderboard(self, group, prev_week):
        url_fmt = "https://www.strava.com/clubs/{}/leaderboard{}"
        addition = "?week_offset=1" if prev_week else ""
        url = url_fmt.format(group, addition)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": url,
        }

        r = self.session.get(url, headers=headers)
        if r.status_code != 200:
            log.warning(f"Error reading leaderboard for {group}")
            return []

        data = json.loads(r.text)
        return list(
            sorted(
                map(
                    lambda ath: {
                        "id": ath["athlete_id"],
                        "rank": ath["rank"],
                        "distance": round(ath["distance"] / 1000),
                    },
                    data["data"],
                ),
                key=lambda ath: ath["rank"],
            )
        )

    def _get_name(self, id):
        url_fmt = "https://www.strava.com/athletes/{}"
        url = url_fmt.format(id)

        headers = {"User-Agent": self.user_agent, "Referer": url}

        r = self.session.get(url, headers=headers)
        if r.status_code != 200:
            log.warning(f"Error reading name for {id}")
            return ""

        match = re.search(r"<title>Strava [A-Za-z]* Profile \| (.*)</title>", r.text)
        try:
            return match.group(1)
        except IndexError:
            log.warning(f"Error parsing name for {id}")
        return ""

    @staticmethod
    def enable_logging():
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize log, otherwise you'll not see debug output.
        log.basicConfig()
        log.getLogger().setLevel(log.DEBUG)
        requests_log = log.getLogger("requests.packages.urllib3")
        requests_log.setLevel(log.DEBUG)
        requests_log.propagate = True

    def get_strava_members(self) -> List[str]:
        members = [Member(m, self.get_name(m)) for m in self.storage.get_members()]
        return MemberList.printable(members)
