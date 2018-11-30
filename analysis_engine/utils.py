"""
Date utils
"""

import datetime
import analysis_engine.consts as ae_consts


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
        fmt=ae_consts.COMMON_DATE_FORMAT):
    """get_last_close_str

    Get the Last Trading Close Date as a string
    with default formatting ae_consts.COMMON_DATE_FORMAT
    (YYYY-MM-DD)

    :param fmt: optional output format (default
        ae_consts.COMMON_DATE_FORMAT)
    """
    return last_close().strftime(fmt)
# end of get_last_close_str


def utc_now_str(
        fmt=ae_consts.COMMON_TICK_DATE_FORMAT):
    """utc_now_str

    Get the UTC now as a string
    with default formatting ae_consts.COMMON_TICK_DATE_FORMAT
    (YYYY-MM-DD HH:MM:SS)

    :param fmt: optional output format (default
        ae_consts.COMMON_TICK_DATE_FORMAT)
    """
    return datetime.datetime.utcnow().strftime(
        fmt)
# end of utc_now_str


def utc_date_str(
        fmt=ae_consts.COMMON_DATE_FORMAT):
    """utc_date_str

    Get the UTC date as a string
    with default formatting ``COMMON_DATE_FORMAT``

    :param fmt: optional output format (default
        COMMON_DATE_FORMAT ``YYYY-MM-DD``)
    """
    return datetime.datetime.utcnow().strftime(
        fmt)
# end of utc_date_str


def get_date_from_str(
        date_str,
        fmt=ae_consts.COMMON_TICK_DATE_FORMAT):
    """get_date_from_str

    Convert a date to a string where the
    default date formatting is ``ae_consts.COMMON_TICK_DATE_FORMAT``

    :param date_str: string date value with a format of ``fmt``
    :param fmt: date format ``YYYY-MM-DD HH:MM:SS`` by default
    """

    return datetime.datetime.strptime(
        date_str,
        fmt)
# end of get_date_from_str


def get_trade_open_xticks_from_date_col(
        date_list):
    """get_trade_open_xticks_from_date_col

    Call this to plot date strings in order
    with just the trading open as the xticks

    :param date_list: column from the ``pandas.DataFrame``
        like ``date_list=df['minute']``
    """

    open_of_trading_fmt = '%Y-%m-%d 09:30:00'

    date_strings = []
    date_labels = []

    last_date = None
    final_date = None
    for idx, date in enumerate(date_list):
        new_day = False
        final_date = date
        if not last_date:
            last_date = date
            next_open_of_trading = datetime.datetime.strptime(
                (date + datetime.timedelta(days=1)).strftime(
                    open_of_trading_fmt),
                ae_consts.COMMON_TICK_DATE_FORMAT)
            new_day = True
        else:
            if date > last_date and date > next_open_of_trading:
                new_day = True
                last_date = date
                next_open_of_trading = datetime.datetime.strptime(
                    (date + datetime.timedelta(days=1)).strftime(
                        open_of_trading_fmt),
                    ae_consts.COMMON_TICK_DATE_FORMAT)
        if new_day:
            date_strings.append(
                date.strftime(ae_consts.COMMON_TICK_DATE_FORMAT))
            date_labels.append(
                date.strftime('%m-%d %H:30'))
        # end of adding new day
    # end of for all dates to find the opens

    if final_date:
        should_add_last_point = False
        if final_date > last_date:
            should_add_last_point = True

        if should_add_last_point:
            date_strings.append(
                final_date.strftime(ae_consts.COMMON_TICK_DATE_FORMAT))
            date_labels.append(
                final_date.strftime('%m-%d %H:%M'))
        # end of adding final point
    # end of adding final point

    return date_strings, date_labels
# end of get_trade_open_xticks_from_date_col
