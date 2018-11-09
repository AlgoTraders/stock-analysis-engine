"""
Build option spread pricing details
"""

from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import TRADE_ENTRY
from analysis_engine.consts import SPREAD_VERTICAL_BULL
from analysis_engine.consts import OPTION_CALL
from analysis_engine.consts import to_f
from analysis_engine.consts import get_status
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def build_option_spread_details(
        trade_type,
        spread_type,
        option_type,
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_option_spread_details

    Calculate pricing information for supported spreads
    including ``max loss``, ``max profit``, and ``mid price`` (break
    even coming soon)

    :param trade_type: entry (``TRADE_ENTRY``) or
        exit (``TRADE_EXIT``) of a spread position
    :param spread_type: vertical bull (``SPREAD_VERTICAL_BULL``)
        and vertical bear (``SPREAD_VERTICAL_BEAR``)
        are the only supported calculations for now
    :param option_type: call (``OPTION_CALL``) or put
        (``OPTION_PUT``)
    :param close: closing price of the underlying
        asset
    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    details = {
        'status': NOT_RUN,
        'trade_type': trade_type,
        'spread_type': spread_type,
        'option_type': option_type,
        'num_contracts': num_contracts,
        'low_strike': low_strike,
        'low_bid': low_bid,
        'low_ask': low_ask,
        'high_strike': high_strike,
        'high_bid': high_bid,
        'high_ask': high_ask,
        'cost': None,
        'revenue': None,
        'low_bidask_mid': None,
        'high_bidask_mid': None,
        'mid_price': None,
        'nat_price': None,
        'strike_width': None,
        'break_even': None,
        'max_loss': None,
        'max_profit': None,
        'spread_id': None
    }

    low_distance = int(close) - low_strike
    high_distance = high_strike - int(close)
    details['strike_width'] = to_f(
        high_strike - low_strike)
    details['spread_id'] = 'S_{}_O_{}_low_{}_high_{}_w_{}'.format(
        trade_type,
        spread_type,
        option_type,
        low_distance,
        high_distance,
        details['strike_width'])
    details['low_bidask_mid'] = to_f(low_bid + low_ask / 2.0)
    details['high_bidask_mid'] = to_f(high_bid + high_ask / 2.0)
    details['mid_price'] = to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))
    details['nat_price'] = to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))

    cost_of_contracts_at_mid_price = None
    revenue_of_contracts_at_mid_price = None

    if trade_type == TRADE_ENTRY:
        cost_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * details['mid_price'])
        revenue_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == SPREAD_VERTICAL_BULL:
            if option_type == OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
        else:  # bear
            if option_type == OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price

    else:  # trade exit calculations:
        revenue_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * details['mid_price'])
        cost_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == SPREAD_VERTICAL_BULL:
            if option_type == OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
        else:  # bear
            if option_type == OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
    # end of supported types of spreads

    details['cost'] = cost_of_contracts_at_mid_price
    details['revenue'] = revenue_of_contracts_at_mid_price

    log.debug(
        'type={} spread={} option={} close={} spread_id={} '
        'revenue={} cost={} mid={} width={} '
        'max_profit={} max_loss={}'.format(
            get_status(status=trade_type),
            get_status(status=spread_type),
            get_status(status=option_type),
            close,
            details['spread_id'],
            revenue_of_contracts_at_mid_price,
            cost_of_contracts_at_mid_price,
            details['mid_price'],
            details['strike_width'],
            details['max_profit'],
            details['max_loss']))

    return details
# end of build_option_spread_details
