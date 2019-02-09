"""
Date utils
"""

import datetime
import analysis_engine.consts as ae_consts


def last_close():
    """last_close

    Get last trading close time as a python ``datetime``

    How it works:

    - During market hours the returned ``datetime`` will be
        ``datetime.datetime.utcnow() - datetime.timedelta(hours=5)``
    - Before or after market hours, the returned ``datetime``
        will be 4:00 PM EST on the previous trading day which
        could be a Friday if this is called on a Saturday or Sunday.

    .. note:: does not detect holidays and non-trading
        days yet and assumes the system time is
        set to EST or UTC
    """
    now = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=5))
    today = now.date()
    close = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=16)
    market_start_time = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=9,
        minute=30,
        second=0)
    market_end_time = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=16,
        minute=0,
        second=0)

    if today.weekday() == 5:
        return close - datetime.timedelta(days=1)
    elif today.weekday() == 6:
        return close - datetime.timedelta(days=2)
    elif market_start_time <= now <= market_end_time:
        return now
    else:
        if now.hour < 16:
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


def convert_epoch_to_datetime_string(
        epoch,
        fmt=ae_consts.COMMON_TICK_DATE_FORMAT,
        use_utc=True):
    """convert_epoch_to_datetime_string

    :param epoch: integer epoch time value
    :param fmt: optional string date format
    :param use_utc: if utc or local time - default is ``True``
    """

    if use_utc:
        return datetime.datetime.utcfromtimestamp(epoch).strftime(fmt)
    else:
        return datetime.datetime.fromtimestamp(epoch).strftime(fmt)
# end of convert_epoch_to_datetime_string


def epoch_to_dt(
        epoch,
        use_utc=False,
        convert_to_est=True):
    """epoch_to_dt

    Convert epoch milliseconds to datetime

    :param epoch: integer milliseconds
    :param use_utc: boolean to convert from ``UTC``
        default is ``False``
    :param convert_to_est: boolean to convert from
        ``UTC`` to ``EST``
    """

    converted_time = None
    if use_utc:
        converted_time = datetime.datetime.utcfromtimestamp(
            epoch)
    else:
        converted_time = datetime.datetime.fromtimestamp(
            epoch)
    # if/else

    if convert_to_est:
        converted_time = (
            converted_time - datetime.timedelta(hours=5))

    return converted_time
# end of epoch_to_dt


def get_days_between_dates(
        from_historical_date,
        last_close_to_use=None):
    """get_days_between_dates

    :param from_historical_date: historical date in time to start walking
                                 forward until the last close datetime
    :param last_close_to_use: starting date in time (left leg of window)
    """
    use_last_close = last_close_to_use
    if not use_last_close:
        use_last_close = last_close()

    dates = []
    while from_historical_date < last_close_to_use:
        dates.append(from_historical_date)
        from_historical_date += datetime.timedelta(
            days=1)
    return dates
# end of get_days_between_dates
