"""
Common and constants

Supported environment variables:

::

    export DEFAULT_FETCH_DATASETS="daily,minute,tick,stats,
peers,news,financials,earnings,dividends,company"

"""

import os
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


FETCH_DAILY = 800
FETCH_MINUTE = 801
FETCH_TICK = 802
FETCH_STATS = 803
FETCH_PEERS = 804
FETCH_NEWS = 805
FETCH_FINANCIALS = 806
FETCH_EARNINGS = 807
FETCH_DIVIDENDS = 808
FETCH_COMPANY = 809

DATAFEED_DAILY = 900
DATAFEED_MINUTE = 901
DATAFEED_TICK = 902
DATAFEED_STATS = 903
DATAFEED_PEERS = 904
DATAFEED_NEWS = 905
DATAFEED_FINANCIALS = 906
DATAFEED_EARNINGS = 907
DATAFEED_DIVIDENDS = 908
DATAFEED_COMPANY = 909

DEFAULT_FETCH_DATASETS = [
    FETCH_DAILY,
    FETCH_MINUTE,
    FETCH_TICK,
    FETCH_STATS,
    FETCH_PEERS,
    FETCH_NEWS,
    FETCH_FINANCIALS,
    FETCH_EARNINGS,
    FETCH_DIVIDENDS,
    FETCH_COMPANY
]
TIMESENSITIVE_DATASETS = [
    FETCH_MINUTE,
    FETCH_TICK,
    FETCH_NEWS
]

ENV_FETCH_DATASETS = os.getenv(
    'DEFAULT_FETCH_DATASETS',
    None)
FETCH_DATASETS = DEFAULT_FETCH_DATASETS
if ENV_FETCH_DATASETS:
    FETCH_DATASETS = ENV_FETCH_DATASETS.split(',')


def get_ft_str(
        ft_type):
    """get_ft_str

    :param ft_type: enum fetch type value to return
                    as a string
    """
    if ft_type == FETCH_DAILY:
        return 'daily'
    elif ft_type == FETCH_MINUTE:
        return 'minute'
    elif ft_type == FETCH_TICK:
        return 'tick'
    elif ft_type == FETCH_STATS:
        return 'stats'
    elif ft_type == FETCH_PEERS:
        return 'peers'
    elif ft_type == FETCH_NEWS:
        return 'news'
    elif ft_type == FETCH_FINANCIALS:
        return 'financials'
    elif ft_type == FETCH_EARNINGS:
        return 'earnings'
    elif ft_type == FETCH_DIVIDENDS:
        return 'dividends'
    elif ft_type == FETCH_COMPANY:
        return 'company'
    else:
        return 'unsupported ft_type={}'.format(
            ft_type)
# end of get_ft_str


def get_datafeed_str(
        df_type):
    """get_datafeed_str

    :param df_type: enum fetch type value to return
                    as a string
    """
    if df_type == DATAFEED_DAILY:
        return 'daily'
    elif df_type == DATAFEED_MINUTE:
        return 'minute'
    elif df_type == DATAFEED_TICK:
        return 'tick'
    elif df_type == DATAFEED_STATS:
        return 'stats'
    elif df_type == DATAFEED_PEERS:
        return 'peers'
    elif df_type == DATAFEED_NEWS:
        return 'news'
    elif df_type == DATAFEED_FINANCIALS:
        return 'financials'
    elif df_type == DATAFEED_EARNINGS:
        return 'earnings'
    elif df_type == DATAFEED_DIVIDENDS:
        return 'dividends'
    elif df_type == DATAFEED_COMPANY:
        return 'company'
    else:
        return 'unsupported df_type={}'.format(
            df_type)
# end of get_datafeed_str
