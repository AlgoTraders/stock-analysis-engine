"""
Common and constants

Supported environment variables:

::

    export DEFAULT_FETCH_DATASETS_YAHOO="pricing_yahoo,options_yahoo,
    news_yahoo"

"""

import os
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


FETCH_PRICING_YAHOO = 1000
FETCH_OPTIONS_YAHOO = 1001
FETCH_NEWS_YAHOO = 1002

DATAFEED_PRICING_YAHOO = 1100
DATAFEED_OPTIONS_YAHOO = 1101
DATAFEED_NEWS_YAHOO = 1102

DEFAULT_FETCH_DATASETS_YAHOO = [
    FETCH_PRICING_YAHOO,
    FETCH_OPTIONS_YAHOO,
    FETCH_NEWS_YAHOO
]
TIMESENSITIVE_DATASETS_YAHOO = [
    FETCH_PRICING_YAHOO,
    FETCH_OPTIONS_YAHOO,
    FETCH_NEWS_YAHOO
]

ENV_FETCH_DATASETS_YAHOO = os.getenv(
    'DEFAULT_FETCH_DATASETS_YAHOO',
    None)
FETCH_DATASETS_YAHOO = DEFAULT_FETCH_DATASETS_YAHOO
if ENV_FETCH_DATASETS_YAHOO:
    FETCH_DATASETS_YAHOO = \
        ENV_FETCH_DATASETS_YAHOO.split(',')


def get_ft_str_yahoo(
        ft_type):
    """get_ft_str_yahoo

    :param ft_type: enum fetch type value to return
                    as a string
    """
    if ft_type == FETCH_PRICING_YAHOO:
        return 'pricing_yahoo'
    elif ft_type == FETCH_OPTIONS_YAHOO:
        return 'options_yahoo'
    elif ft_type == FETCH_NEWS_YAHOO:
        return 'news_yahoo'
    else:
        return f'unsupported ft_type={ft_type}'
# end of get_ft_str_yahoo


def get_datafeed_str_yahoo(
        df_type):
    """get_datafeed_str_yahoo

    :param df_type: enum fetch type value to return
                    as a string
    """
    if df_type == DATAFEED_PRICING_YAHOO:
        return 'pricing_yahoo'
    elif df_type == DATAFEED_OPTIONS_YAHOO:
        return 'options_yahoo'
    elif df_type == DATAFEED_NEWS_YAHOO:
        return 'news_yahoo'
    else:
        return f'unsupported df_type={df_type}'
# end of get_datafeed_str_yahoo
