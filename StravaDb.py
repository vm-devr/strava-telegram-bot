import sqlite3
from datetime import datetime

from LeaderBoard import LeaderBoard
from logger import log


class StravaDb(LeaderBoard):
    def __init__(self, storage, strava):
        self.storage = storage
        self.strava = strava

    def getLeaderboard(self, prevYear, all, elements):
        log.info("Reading latest leaderboard")

        if elements > 99:
            elements = 99

        members = self.storage.getMembers()
        conn = sqlite3.connect("../grc_perl/grc.db")
        raw_board = []
        cursor = conn.cursor()
        query_fmt = (
            'SELECT id, name, CAST(ROUND(dst_{year}) as INT) As "distance" FROM athletes ORDER BY dst_{year} DESC;'
        )
        query = query_fmt.format(year=self.getYear(prevYear, all))
        for row in cursor.execute(query):
            raw_board.append({"id": row[0], "name": row[1], "distance": row[2]})

        filtered_board = list(filter(lambda ath: ath["id"] in members, raw_board))
        board = filtered_board[:elements]

        return self.printable(board, 5)

    def getYear(self, prevYear, all):
        if all:
            return "all"

        today = datetime.today()
        if prevYear:
            return str(today.year - 1)

        return str(today.year)

    def getBoard(self, is_all, is_year, is_month, is_previous, elements):
        log.info("Reading latest leaderboard from db")

        if elements > 99:
            elements = 99

        members = self.storage.getMembers()
        conn = sqlite3.connect("../grc_perl/grc.db")
        raw_board = []
        cursor = conn.cursor()
        query = ""
        dist_num = 3
        if is_all:
            query = "select * from athletes_stats order by processed desc;"
            dist_num = 5
        elif is_year:
            year = datetime.today().year
            if is_previous:
                year = year - 1
            year_next = year + 1
            query_fmt = (
                'select * from athletes_stats where processed like "{year}%" or '
                'processed like "{year_next}-01-01%" order by processed desc;'
            )
            query = query_fmt.format(year=year, year_next=year_next)
            dist_num = 5
        elif is_month:
            month = datetime.today().month
            year = datetime.today().year
            if is_previous:
                month = month - 1
            month_next = month + 1
            query_fmt = (
                'select * from athletes_stats where processed like "{year}-0{month}%" or '
                'processed like "{year}-0{month_next}-01%" order by processed desc;'
            )
            query = query_fmt.format(year=year, month=month, month_next=month_next)
            log.info(query)

        board_dict = {}
        for row in cursor.execute(query):
            athlete_id = row[1]
            dist = row[2]
            if athlete_id in board_dict:
                board_dict[athlete_id]["distance_total"] = board_dict[athlete_id]["distance_end"] - dist
            else:
                board_dict[athlete_id] = {"distance_total": 0, "distance_end": dist}
        raw_board = []
        for key in board_dict:
            value = board_dict[key]
            distance = int(value["distance_total"])
            if is_all:
                distance = int(value["distance_end"])
            raw_board.append({"id": key, "name": self.strava.getName(key), "distance": distance})

        def takeTotal(elem):
            return elem["distance"]

        raw_board.sort(key=takeTotal, reverse=True)

        filtered_board = list(filter(lambda ath: ath["id"] in members, raw_board))

        board = filtered_board[:elements]
        return self.printable(board, dist_num)
