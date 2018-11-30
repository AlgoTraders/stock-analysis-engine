try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests
import tornado
import ujson
import pandas as pd
import pyEX as p
import string
import warnings
warnings.filterwarnings("ignore")  # noqa
from spylunking.log.setup_logging import build_colorized_logger
from trading_calendars import get_calendar
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta


_TRANSLATOR = str.maketrans('', '', string.punctuation)
_OVERRIDES = {
    'PCLN': 'BKNG'
}

log = build_colorized_logger(
    name=__name__)


def parse_args(argv):
    args = []
    kwargs = {}
    for arg in argv:
        if '--' not in arg and '-' not in arg:
            log.debug('ignoring argument: %s', arg)
            continue
        if '=' in arg:
            k, v = arg.replace('-', '').split('=')
            kwargs[k] = v
        else:
            args.append(arg.replace('-', ''))
    return args, kwargs


def parse_body(req, **fields):
    try:
        data = tornado.escape.json_decode(req.body)
    except ValueError:
        data = {}
    return data


def safe_get(path, *args, **kwargs):
    try:
        log.debug('GET: %s' % path)
        resp = requests.get(path, *args, **kwargs).text
        # log.debug('GET_RESPONSE: %s' % resp)
        return ujson.loads(resp)
    except ConnectionRefusedError:
        return {}


def safe_post(path, *args, **kwargs):
    try:
        log.debug('POST: %s' % path)
        resp = requests.post(path, *args, **kwargs).text
        # log.debug('POST_RESPONSE: %s' % resp)
        return ujson.loads(resp)
    except ConnectionRefusedError:
        return {}


def safe_post_cookies(path, *args, **kwargs):
    try:
        log.debug('POST: %s' % path)
        resp = requests.post(path, *args, **kwargs)
        # log.debug('POST_RESPONSE: %s' % resp.text)
        return ujson.loads(resp.text), resp.cookies
    except ConnectionRefusedError:
        return {}, None


def construct_path(host, method):
    return urljoin(host, method)


def symbols():
    return p.symbolsDF().index.values.tolist()


def symbols_map():
    ret = {}
    for x in symbols():
        ret[x] = x
        new_x = x.translate(_TRANSLATOR)
        if new_x not in ret:
            ret[new_x] = x
    for k, v in _OVERRIDES.items():
        ret[k] = v
    return ret


def today():
    """today starts at 4pm the previous close"""
    today = date.today()
    return datetime(
        year=today.year,
        month=today.month,
        day=today.day)


def this_week():
    """start of week"""
    return today() - timedelta(days=datetime.today().isoweekday() % 7)


def last_close():
    """last close"""
    today = date.today()
    close = datetime(
        year=today.year,
        month=today.month,
        day=today.day, hour=16)

    if today.weekday() == 5:
        return close - timedelta(days=1)
    elif today.weekday() == 6:
        return close - timedelta(days=2)
    else:
        if datetime.now().hour < 16:
            close -= timedelta(days=1)
            if close.weekday() == 5:  # saturday
                return close - timedelta(days=1)
            elif close.weekday() == 6:  # sunday
                return close - timedelta(days=2)
            return close
        return close


def yesterday():
    """yesterday is anytime before the previous 4pm close"""
    today = date.today()

    if today.weekday() == 0:  # monday
        return datetime(
            year=today.year,
            month=today.month,
            day=today.day) - timedelta(days=3)
    elif today.weekday() == 6:  # sunday
        return datetime(
            year=today.year,
            month=today.month,
            day=today.day) - timedelta(days=2)
    return datetime(
        year=today.year,
        month=today.month,
        day=today.day) - timedelta(days=1)


def last_month():
    """last_month is one month before today"""
    today = date.today()
    last_month = datetime(
        year=today.year,
        month=today.month,
        day=today.day) - relativedelta(months=1)

    if last_month.weekday() == 5:
        last_month -= timedelta(days=1)
    elif last_month.weekday() == 6:
        last_month -= timedelta(days=2)
    return last_month


def six_months():
    """six_months is six months before today"""
    today = date.today()
    six_months = datetime(
        year=today.year,
        month=today.month,
        day=today.day) - relativedelta(months=6)

    if six_months.weekday() == 5:
        six_months -= timedelta(days=1)
    elif six_months.weekday() == 6:
        six_months -= timedelta(days=2)
    return six_months


def three_months():
    """three_months"""
    today = date.today()
    six_months = datetime(
        year=today.year,
        month=today.month,
        day=today.day) - relativedelta(months=3)

    if six_months.weekday() == 5:
        six_months -= timedelta(days=1)
    elif six_months.weekday() == 6:
        six_months -= timedelta(days=2)
    return six_months


def never():
    """never"""
    return datetime(
        year=1,
        month=1,
        day=1)


def append(df1, df2):
    """append

    :param df1:
    :param df2:
    """
    merged = pd.concat([df1, df2])
    return merged[~merged.index.duplicated(keep='first')]


def holidays():
    """holidays"""
    return get_calendar(
        'NYSE').regular_holidays.holidays().to_pydatetime().tolist()


def business_days(start, end=last_close()):
    """business_days"""
    ret = []
    while start < last_close():
        is_a_business_day = (
            start not in holidays() and
            start.weekday() != 6 and start.weekday() != 5)
        if is_a_business_day:
            ret.append(start)
        start += timedelta(days=1)
    return ret


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
