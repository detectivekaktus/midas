from json import loads
from logging import getLogger
from logging.config import dictConfig
from os import getcwd, mkdir, path


def load_logging_config() -> None:
    with open("logging.conf.json", "r") as f:
        content = f.read()

    conf = loads(content)

    if not path.exists(path.join(getcwd(), "logs")):
        mkdir("logs")

    dictConfig(config=conf)


aiogram_logger = getLogger("aiogram")
app_logger = getLogger("app")

__all__ = ("aiogram_logger", "app_logger")
