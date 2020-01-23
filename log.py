# -*- coding: utf-8 -*-

# Logging module

import sys
from enum import Enum
from typing import TextIO


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4  # Raises an exception


SEVERITY = LogLevel.WARNING
OUTPUT: TextIO = sys.stderr
ERROR_COUNT = 0
MAX_ERRORS_ALLOWED = 1


class CriticalError(BaseException):
    pass


def log(msg: str, loglevel: LogLevel = None):
    global SEVERITY
    global ERROR_COUNT

    if loglevel is None:
        loglevel = SEVERITY

    message = "{}: {}".format(str(loglevel), msg)
    if loglevel >= SEVERITY:
        OUTPUT.write(message + '\n')

    if loglevel >= LogLevel.ERROR:
        ERROR_COUNT += 1
        if ERROR_COUNT >= MAX_ERRORS_ALLOWED:
            sys.exit(1)

    if loglevel >= LogLevel.CRITICAL:
        raise CriticalError(msg)


def error(msg: str):
    log(msg, LogLevel.ERROR)
