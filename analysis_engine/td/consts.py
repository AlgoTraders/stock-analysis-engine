"""
Tradier Consts, Environment Variables and Authentication
Helper
"""

import os
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)

TD_ENDPOINT_API = os.getenv(
    'TD_ENDPOINT_API',
    'api.tradier.com')
TD_ENDPOINT_DATA = os.getenv(
    'TD_ENDPOINT_DATA',
    'sandbox.tradier.com')
TD_ENDPOINT_STREAM = os.getenv(
    'TD_ENDPOINT_STREAM',
    'sandbox.tradier.com')
TD_TOKEN = os.getenv(
    'TD_TOKEN',
    'MISSING_TD_TOKEN')
TD_URLS = {
    'account': (
        f'https://{TD_ENDPOINT_DATA}'
        '/v1/user/profile'),
    'options': (
        f'https://{TD_ENDPOINT_DATA}'
        '/v1/markets/options/chains'
        f'?symbol={"{}"}&expiration={"{}"}')
}

FETCH_TD_CALLS = 10000
FETCH_TD_PUTS = 10001

DATAFEED_TD_CALLS = 11000
DATAFEED_TD_PUTS = 11001

DEFAULT_FETCH_DATASETS_TD = [
    FETCH_TD_CALLS,
    FETCH_TD_PUTS
]
TIMESENSITIVE_DATASETS_TD = [
    FETCH_TD_CALLS,
    FETCH_TD_PUTS
]

ENV_FETCH_DATASETS_TD = os.getenv(
    'ENV_FETCH_DATASETS_TD',
    None)
if ENV_FETCH_DATASETS_TD:
    SPLIT_FETCH_DATASETS_TD = \
        ENV_FETCH_DATASETS_TD.split(',')
    DEFAULT_FETCH_DATASETS_TD = []
    for d in SPLIT_FETCH_DATASETS_TD:
        if d == 'tdcalls':
            DEFAULT_FETCH_DATASETS_TD.append(
                FETCH_TD_CALLS)
        elif d == 'tdputs':
            DEFAULT_FETCH_DATASETS_TD.append(
                FETCH_TD_PUTS)
# end of handling custom ENV_FETCH_DATASETS_TD

FETCH_DATASETS_TD = DEFAULT_FETCH_DATASETS_TD

TD_OPTION_COLUMNS = [
    'ask',
    'ask_date',
    'asksize',
    'bid',
    'bid_date',
    'bidsize',
    'date',
    'exp_date',
    'last',
    'last_volume',
    'open_interest',
    'opt_type',
    'strike',
    'ticker',
    'trade_date',
    'created',
    'volume'
]

TD_EPOCH_COLUMNS = [
    'ask_date',
    'bid_date',
    'trade_date'
]


def get_ft_str_td(
        ft_type):
    """get_ft_str_td

    :param ft_type: enum fetch type value to return
                    as a string
    """
    if ft_type == FETCH_TD_CALLS:
        return 'tdcalls'
    elif ft_type == FETCH_TD_PUTS:
        return 'tdputs'
    else:
        return f'unsupported ft_type={ft_type}'
# end of get_ft_str_td


def get_datafeed_str_td(
        df_type):
    """get_datafeed_str_td

    :param df_type: enum fetch type value to return
                    as a string
    """
    if df_type == DATAFEED_TD_CALLS:
        return 'tdcalls'
    elif df_type == DATAFEED_TD_PUTS:
        return 'tdputs'
    else:
        return f'unsupported df_type={df_type}'
# end of get_datafeed_str_td


def get_auth_headers(
        use_token=TD_TOKEN,
        env_token=None):
    """get_auth_headers

    Get connection and auth headers for Tradier account:
    https://developer.tradier.com/getting_started

    :param use_token: optional - token
        instead of the default ``TD_TOKEN``
    :param env_token: optional - env key to use
        instead of the default ``TD_TOKEN``
    """
    token = TD_TOKEN
    if env_token:
        token = os.getenv(
            env_token,
            TD_TOKEN)
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    return headers
# end of get_auth_headers
