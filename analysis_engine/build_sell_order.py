"""
Helper for creating a sell order
"""

import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_sell_order(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        details,
        use_key,
        minute=None,
        shares=None,
        version=1,
        auto_fill=True,
        is_live_trading=False,
        backtest_shares_default=10,
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
    :param minute: optional - string with the minute that the
        order was placed. format is
        ``COMMON_TICK_DATE_FORMAT`` (``YYYY-MM-DD HH:MM:SS``)
    :param details: dictionary for full row of values to review
        all sells after the algorithm finishes.
        (usually ``row.to_json()``)
    :param use_key: string for redis and s3 publishing of the algorithm
        result dictionary as a json-serialized dictionary
    :param shares: optional - integer number of shares to sell
        if None sell all ``num_owned`` shares at the ``close``.
    :param version: optional - version tracking integer
    :param auto_fill: optional - bool for not assuming the trade
        filled (default ``True``)
    :param is_live_trading: optional - bool for filling trades
        for live trading or for backtest tuning filled
        (default ``False`` which is backtest mode)
    :param backtest_shares_default: optional - integer for
        simulating shares during a backtest even if there
        are not enough funds
        (default ``10``)
    :param reason: optional - string for recording why the algo
        decided to sell for review after the algorithm finishes
    """
    status = ae_consts.TRADE_OPEN
    s3_bucket_name = ae_consts.ALGO_SELLS_S3_BUCKET_NAME
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
        status = ae_consts.TRADE_NO_SHARES_TO_SELL
    elif close > 0.1 and tradable_funds > 10.0:
        cost_of_trade = commission
        if shares:
            if shares > num_owned:
                shares = num_owned
        else:
            shares = num_owned
        sell_price = ae_consts.to_f(
            val=(shares * close) + commission)
        if cost_of_trade > balance:
            status = ae_consts.TRADE_NOT_ENOUGH_FUNDS
        else:
            created_date = ae_utils.utc_now_str()
            if auto_fill:
                new_shares = num_owned - shares
                new_balance = ae_consts.to_f(balance + sell_price)
                status = ae_consts.TRADE_FILLED
            else:
                new_shares = shares
                new_balance = balance
    else:
        status = ae_consts.TRADE_NOT_ENOUGH_FUNDS

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
        'minute': minute,
        'created': created_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'version': version
    }

    use_date = minute
    if not use_date:
        use_date = date

    log.debug(
        f'{ticker} {use_date} sell '
        f'{ae_consts.get_status(status=order_dict["status"])} '
        f'order={ae_consts.ppj(order_dict)}')

    return order_dict
# end of build_sell_order
