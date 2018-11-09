"""
Helper for creating a sell order
"""

from analysis_engine.consts import TRADE_OPEN
from analysis_engine.consts import TRADE_NOT_ENOUGH_FUNDS
from analysis_engine.consts import TRADE_NO_SHARES_TO_SELL
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import ALGO_SELLS_S3_BUCKET_NAME
from analysis_engine.consts import to_f
from analysis_engine.consts import get_status
from analysis_engine.consts import ppj
from analysis_engine.utils import utc_now_str
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def build_sell_order(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        details,
        use_key,
        shares=None,
        version=1,
        auto_fill=True,
        reason=None):
    """build_sell_order

    Create an algorithm sell order as a dictionary

    :param ticker: ticker
    :param num_owned: integer current owned
        number of shares for this asset
    :param close: float closing price of the asset
    :param balance: float amount of available capital
    :param commission: float for commission costs
    :param date: string trade date for that row usually
        ``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param details: dictionary for full row of values to review
        all sells after the algorithm finishes. (usually ``row.to_json()``)
    :param use_key: string for redis and s3 publishing of the algorithm
        result dictionary as a json-serialized dictionary
    :param shares: optional - integer number of shares to sell
        if None sell all ``num_owned`` shares at the ``close``.
    :param version: optional - version tracking integer
    :param auto_fill: optional - bool for not assuming the trade
        filled (default ``True``)
    :param reason: optional - string for recording why the algo
        decided to sell for review after the algorithm finishes
    """
    status = TRADE_OPEN
    s3_bucket_name = ALGO_SELLS_S3_BUCKET_NAME
    s3_key = use_key
    redis_key = use_key
    s3_enabled = True
    redis_enabled = True

    cost_of_trade = None
    sell_price = 0.0
    new_shares = num_owned
    new_balance = balance
    created_date = None

    tradable_funds = balance - commission

    if num_owned == 0:
        status = TRADE_NO_SHARES_TO_SELL
    elif close > 0.1 and tradable_funds > 10.0:
        cost_of_trade = commission
        if shares:
            if shares > num_owned:
                shares = num_owned
        else:
            shares = num_owned
        sell_price = to_f(
            val=(shares * close) + commission)
        if cost_of_trade > balance:
            status = TRADE_NOT_ENOUGH_FUNDS
        else:
            created_date = utc_now_str()
            if auto_fill:
                new_shares = num_owned - shares
                new_balance = to_f(balance + sell_price)
                status = TRADE_FILLED
            else:
                new_shares = shares
                new_balance = balance
    else:
        status = TRADE_NOT_ENOUGH_FUNDS

    order_dict = {
        'ticker': ticker,
        'status': status,
        'balance': new_balance,
        'shares': new_shares,
        'sell_price': sell_price,
        'prev_balance': balance,
        'prev_shares': num_owned,
        'close': close,
        'details': details,
        'reason': reason,
        'date': date,
        'created': created_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'version': version
    }

    log.debug(
        '{} {} sell {} order={}'.format(
            ticker,
            date,
            get_status(status=order_dict['status']),
            ppj(order_dict)))

    return order_dict
# end of build_sell_order
