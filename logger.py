import logging
from pythonjsonlogger import json

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Initialize the logger object with a name dependent on the call file.

    :param name: the name of the module that is currently being logged
    :return: Logger-object
    """

    # creating a logger with the name
    logger = logging.getLogger(name)

    # creating a minimum level of logs
    logger.setLevel(logging.INFO)

    # log format for console
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # output logs to console
    console_handler = logging.StreamHandler()

    # format initiation
    console_handler.setFormatter(console_formatter)

    # connecting the handler to the logger
    logger.addHandler(console_handler)

    # log format for json
    json_formatter = json.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # writing logs to a file
    file_handler = logging.FileHandler("bot.json.log", encoding="utf-8")

    # format initiation
    file_handler.setFormatter(json_formatter)

    # connecting the handler to the logger
    logger.addHandler(file_handler)

    return logger


# logger object declaration
logger = setup_logger(__name__)