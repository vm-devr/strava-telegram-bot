import json
import time
from dataclasses import dataclass

import telepot
import telepot.loop
from envclasses import envclass
from logger import log
from storage import Storage
from strava import Strava


@envclass
@dataclass
class Config:
    strava_users_config: str = ""
    strava_group: int = 8080
    bot_api_key: str = ""


class Bot:
    def __init__(self, config: Config) -> None:
        log.info("Initializing data")
        storage = Storage(config.strava_users_config)
        self.strava = Strava(storage, config.strava_group)
        self.bot = telepot.Bot(config.bot_api_key)
        self.last_rank_cmd = 0

    def run(self) -> None:
        telepot.loop.GetUpdatesLoop(self.bot, self.handle).run_forever()

    def handle(self, msg) -> None:
        log.info(json.dumps(msg, sort_keys=True, indent=4))

        if (msg is None) or ("message" not in msg.keys()):
            return

        message = msg["message"]
        if ("message_id" not in message.keys()) or ("text" not in message.keys()):
            return

        command_all = message["text"]
        command_line = list(filter(lambda x: len(x) > 0, command_all.split(" ")))
        if len(command_line) < 1:
            return

        chat = message["chat"]
        command = command_line[0]
        chat_id = chat["id"]
        ret = None
        log.info(f"Processing {command_all} for {chat_id}")

        if command.startswith("/rank"):
            one_per = 10
            if time.time() - self.last_rank_cmd < one_per:
                ret = "Вас багато, а я один! Не більше однієї команди на {} секунд".format(one_per)
            else:
                self.last_rank_cmd = time.time()

                count = 50
                if command == "/rank":
                    board = self.strava.get_leaderboard(prev_week=False, elements=count)
                elif command == "/rank_previous":
                    board = self.strava.get_leaderboard(prev_week=True, elements=count)
                elif command == "/rank_10":
                    board = self.strava.get_leaderboard(prev_week=False, elements=10)
                else:
                    board = []

                if not board:
                    board = ["тут поки ніхто не бігав"]
                ret = "<pre>" + "\n".join(board) + "</pre>"
        elif command == "/members":
            members = self.strava.get_strava_members()
            ret = "\n".join(members)
        else:
            ret = None  # u'Не зовсім зрозумів запитання, я поки вчуся та знаю лише /rank команду'

        if ret is not None:
            log.info(f"Sending back {ret}")
            self.bot.sendMessage(chat_id, ret, parse_mode="HTML")
        else:
            log.info("Do not send anything back")
