import logging
import time
from functools import wraps


def getAppLogger():
    return logging.getLogger("quart.app")


def getServerLogger():
    return logging.getLogger("quart.server")


def log_method_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = getAppLogger()
        starting_timestamp = time.time()
        logger.info(f"*********** {func.__name__} method started ***********")
        output = func(*args, **kwargs)
        finish_timestamp = time.time()
        tsm_diff = finish_timestamp - starting_timestamp
        logger.info(
            f"*********** {func.__name__} method succeeded in {tsm_diff} ***********"
        )
        return output

    return wrapper
