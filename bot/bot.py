import json
from dataclasses import dataclass

import telepot
import telepot.loop
from envclasses import envclass
from logger import log
from ratelimiter import RateLimiter
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
        if not command_line:
            return

        chat = message["chat"]
        command = command_line[0]
        chat_id = chat["id"]
        log.info(f"Processing {command_all} for {chat_id}")

        ret = None
        if command.startswith("/rank"):
            ret = self.handle_rank(command)
        elif command == "/members":
            ret = self.handle_members()

        if not ret:
            log.info("Do not send anything back")
            return

        log.info(f"Sending back {ret}")
        self.bot.sendMessage(chat_id, ret, parse_mode="HTML")

    @RateLimiter(max_calls=1, period=10)  # one command per 10 seconds
    def handle_rank(self, command: str) -> str:
        count = 50
        board = []
        match command:
            case "/rank":
                board = self.strava.get_leaderboard(prev_week=False, elements=count)
            case "/rank_10":
                board = self.strava.get_leaderboard(prev_week=False, elements=10)
            case "/rank_previous":
                board = self.strava.get_leaderboard(prev_week=True, elements=count)

        if not board:
            board = ["тут поки ніхто не бігав"]

        return "<pre>" + "\n".join(board) + "</pre>"

    def handle_members(self):
        return "\n".join(self.strava.get_strava_members())
