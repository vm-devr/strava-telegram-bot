import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from envclasses import load_env
from logger import log

from bot import Bot, Config


def run_http_server(port: int) -> None:
    try:
        server_address = ("", port)
        log.info(f"Running HTTP server on address: {server_address}")
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        httpd.serve_forever()
    except BrokenPipeError:
        # See https://docs.python.org/3/library/signal.html#note-on-sigpipe
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)


def str2bool(v: str) -> bool:
    return v.lower() in ("true", "1")


def str2int(v: str, default: int) -> int:
    return int(v) if v else default


def main():
    config = Config()
    load_env(config, prefix="")

    port = str2int(os.getenv("PORT"), 8080)
    Thread(target=run_http_server, args=(port,)).start()

    # This is needed to temporarily disable the Telegram bot on a Cloud to run on a local machine.
    if not str2bool(str(os.getenv("BOT_IS_DISABLED"))):
        bot = Bot(config)
        Thread(target=bot.run).start()


if __name__ == "__main__":
    main()
