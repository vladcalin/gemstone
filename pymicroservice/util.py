import sys
import logging


def init_default_logger():
    logging.basicConfig(
        level=logging.DEBUG,
    )
    return logging.getLogger()
