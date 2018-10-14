"""
Date utils
"""

import datetime
from functools import lru_cache
from analysis_engine.consts import COMMON_DATE_FORMAT
from analysis_engine.consts import COMMON_TICK_DATE_FORMAT


@lru_cache(1)
def last_close():
    """last close

    Get Last Trading Close Date

    .. note:: does not detect holidays and non-trading
              days yet

    last_close - get the last close trading date
    """
    today = datetime.date.today()
    close = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=16)

    if today.weekday() == 5:
        return close - datetime.timedelta(days=1)
    elif today.weekday() == 6:
        return close - datetime.timedelta(days=2)
    else:
        if datetime.datetime.now().hour < 16:
            close -= datetime.timedelta(days=1)
            if close.weekday() == 5:  # saturday
                return close - datetime.timedelta(days=1)
            elif close.weekday() == 6:  # sunday
                return close - datetime.timedelta(days=2)
            return close
        return close
    # if/else
# end of last_close


def get_last_close_str(
        fmt=COMMON_DATE_FORMAT):
    """get_last_close_str

    Get the Last Trading Close Date as a string
    with default formatting COMMON_DATE_FORMAT
    (YYYY-MM-DD)

    :param fmt: optional output format (default
                COMMON_DATE_FORMAT)
    """
    return last_close().strftime(fmt)
# end of get_last_close_str


def utc_now_str(
        fmt=COMMON_TICK_DATE_FORMAT):
    """utc_now_str

    Get the UTC now as a string
    with default formatting COMMON_TICK_DATE_FORMAT
    (YYYY-MM-DD HH:MM:SS)

    :param fmt: optional output format (default
                COMMON_TICK_DATE_FORMAT)
    """
    return datetime.datetime.utcnow().strftime(
        fmt)
# end of utc_now_str


def utc_date_str(
        fmt=COMMON_DATE_FORMAT):
    """utc_date_str

    Get the UTC date as a string
    with default formatting COMMON_DATE_FORMAT
    (YYYY-MM-DD)

    :param fmt: optional output format (default
                COMMON_DATE_FORMAT)
    """
    return datetime.datetime.utcnow().strftime(
        fmt)
# end of utc_date_str
