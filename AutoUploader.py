import json
import os
import re
import time
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

import telepot

import Storage
import Strava
import StravaDb
from logger import log

log.info("Initializing data")
strava_users_config = os.environ["STRAVA_USERS_CONFIG"]
storage = Storage.Storage(strava_users_config)
strava = Strava.Strava(storage)
stravaDb = StravaDb.StravaDb(storage, strava)
bot_api_key = os.environ["BOT_API_KEY"]
bot = telepot.Bot(bot_api_key)
last_rank_cmd = 0
port = int(os.environ["PORT"])


def findTag(reg, command_all):
    match = re.search(reg, command_all)
    try:
        return match.group(1) is not None
    except (IndexError, AttributeError):
        return False


def handle(msg):
    try:
        log.info(json.dumps(msg, sort_keys=True, indent=4))

        if (
            (msg is None)
            or ("chat" not in msg.keys())
            or ("id" not in msg["chat"].keys())
            or ("text" not in msg.keys())
        ):
            return

        command_all = msg["text"]
        command_line = list(filter(lambda x: len(x) > 0, command_all.split(" ")))
        if len(command_line) < 1:
            return

        command = command_line[0]
        chat_id = msg["chat"]["id"]
        ret = None
        log.info(f"Processing {command_all} for {chat_id}")

        if command.startswith("/rank"):
            global last_rank_cmd
            one_per = 10
            if time.time() - last_rank_cmd < one_per:
                ret = "Вас багато, а я один! Не більше однієї команди на {} секунд".format(one_per)
            else:
                last_rank_cmd = time.time()

                prev = findTag(r"\/rank.*(попередн|previous)", command_all)
                year = findTag(r"\/rank.*(рік|year)", command_all)
                month = False  # findTag(r'\/rank.*(місяць|month)', command_all)
                everything = findTag(r"\/rank.*(все|everything|all)", command_all)

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
                    board = stravaDb.getBoard(everything, year, month, prev, count)
                else:
                    board = strava.getLeaderboard(prev, count)
                if len(board) == 0:
                    board = ["тут поки ніхто не бігав"]
                ret = "<pre>" + "\n".join(board) + "</pre>"
        else:
            ret = None  # u'Не зовсім зрозумів запитання, я поки вчуся та знаю лише /rank команду'

        if ret is not None:
            log.info(f"Sending back {ret}")
            bot.sendMessage(chat_id, ret, parse_mode="HTML")
        else:
            log.info("Do not send anything back")
    except Exception:
        log.warning(f"Error processing request {traceback.format_exc()}")


def run_bot():
    bot.message_loop(handle)
    while 1:
        time.sleep(5000)


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
