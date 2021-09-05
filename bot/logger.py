import logging
import os

LOG_FORMAT = "%(levelname)-8s %(filename)s %(funcName)s %(lineno)-5d %(message)s"

level = os.getenv("LOG_LEVEL", logging.DEBUG)

logging.basicConfig(level=level, format=LOG_FORMAT)
log = logging.getLogger(__name__)
