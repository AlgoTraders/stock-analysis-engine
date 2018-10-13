"""
Date utils
"""

import datetime
from functools import lru_cache


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
