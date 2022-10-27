import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

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


def str2int(v: str, default: int) -> int:
    return int(v) if v else default


def main():
    config = Config()
    load_env(config, prefix="")

    bot = Bot(config)
    bot.run_as_thread()

    port = str2int(os.getenv("PORT"), 8080)
    run_http_server(port)


if __name__ == "__main__":
    main()
