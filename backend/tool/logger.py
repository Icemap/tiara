# coding: utf8
from __future__ import absolute_import

import logging
from functools import lru_cache


def init_logger_handler(app):
    logger = app.logger
    logger.setLevel(logging.INFO)

    if app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('''\
--------------------------------------------------------------------------------
[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s [%(pathname)s:%(lineno)d]
%(message)s
--------------------------------------------------------------------------------''')  # noqa: E501
        handler.setFormatter(formatter)
        logger.addHandler(handler)


@lru_cache()
def get_logger(name: str = "tiara", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fmt = logging.Formatter(
        "[%(levelname)s]%(asctime)s.%(process)d#>\
    [%(funcName)s]:%(lineno)s %(message)s"
    )
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger
