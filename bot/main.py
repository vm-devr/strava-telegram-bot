import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from envclasses import load_env
from logger import log

from bot import Bot, Config


def run_http_server(port: int) -> None:
    server_address = ("", port)
    log.info(f"Running HTTP server on address: {server_address}")
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()


def main():
    config = Config()
    load_env(config, prefix="")
    bot = Bot(config)
    Thread(target=bot.run).start()

    port_s = os.getenv("PORT")
    port = int(port_s) if port_s else 8080
    Thread(target=run_http_server, args=(port,)).start()


if __name__ == "__main__":
    main()
