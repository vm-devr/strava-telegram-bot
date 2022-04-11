import json
import os
import re
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from logger import log
from storage import Storage
from strava import Strava
from strava_db import StravaDb
from telepot import Bot
from telepot.loop import GetUpdatesLoop

log.info("Initializing data")
strava_users_config = os.environ["STRAVA_USERS_CONFIG"]
storage = Storage(strava_users_config)
strava_group = int(os.environ["STRAVA_GROUP"])
strava = Strava(storage, strava_group)
strava_db = StravaDb(storage, strava)
bot_api_key = os.environ["BOT_API_KEY"]
bot = Bot(bot_api_key)
last_rank_cmd = 0
port = int(os.environ["PORT"])


def find_tag(reg, command_all):
    match = re.search(reg, command_all)
    try:
        return match.group(1) is not None
    except (IndexError, AttributeError):
        return False


def handle(msg):
    log.info(json.dumps(msg, sort_keys=True, indent=4))

    if (msg is None) or ("message" not in msg.keys()):
        return

    message = msg['message']
    if ("message_id" not in message.keys()) or ("text" not in message.keys()):
        return

    command_all = message["text"]
    command_line = list(filter(lambda x: len(x) > 0, command_all.split(" ")))
    if len(command_line) < 1:
        return

    chat = message['chat']
    command = command_line[0]
    chat_id = chat["id"]
    ret = None
    log.info(f"Processing {command_all} for {chat_id}")

    if command.startswith("/rank"):
        global last_rank_cmd
        one_per = 10
        if time.time() - last_rank_cmd < one_per:
            ret = "Вас багато, а я один! Не більше однієї команди на {} секунд".format(one_per)
        else:
            last_rank_cmd = time.time()

            prev = find_tag(r"\/rank.*(попередн|previous)", command_all)
            year = find_tag(r"\/rank.*(рік|year)", command_all)
            month = False  # findTag(r'\/rank.*(місяць|month)', command_all)
            everything = find_tag(r"\/rank.*(все|everything|all)", command_all)

            count = 0
            match = re.search(r"(\d+)", command_all)
            try:
                count = int(match.group(1))
            except (IndexError, AttributeError):
                count = 0
            if count < 1 or count > 50:
                count = 50

            board = ""
            if year or everything or month:
                board = strava_db.get_board(everything, year, month, prev, count)
            else:
                board = strava.get_leaderboard(prev, count)
            if len(board) == 0:
                board = ["тут поки ніхто не бігав"]
            ret = "<pre>" + "\n".join(board) + "</pre>"
    elif command.startswith("/members"):
        members = strava.get_strava_members()
        ret = "\n".join(members)
    else:
        ret = None  # u'Не зовсім зрозумів запитання, я поки вчуся та знаю лише /rank команду'

    if ret is not None:
        log.info(f"Sending back {ret}")
        bot.sendMessage(chat_id, ret, parse_mode="HTML")
    else:
        log.info("Do not send anything back")


def run_bot():
    GetUpdatesLoop(bot, handle).run_forever()


def run_http_server():
    server_address = ("", port)
    log.info(f"Running HTTP server on address: {server_address}")
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()


def main():
    Thread(target=run_http_server).start()
    Thread(target=run_bot).start()


if __name__ == "__main__":
    main()
