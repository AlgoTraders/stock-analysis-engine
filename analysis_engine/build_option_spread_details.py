"""
Build option spread pricing details
"""

import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


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
        'status': ae_consts.NOT_RUN,
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
    details['strike_width'] = ae_consts.to_f(
        high_strike - low_strike)
    details['spread_id'] = (
        f'T_{trade_type}_S_{spread_type}_O_{option_type}_low_{low_distance}'
        f'_high_{high_distance}_w_{details["strike_width"]}')
    details['low_bidask_mid'] = ae_consts.to_f(low_bid + low_ask / 2.0)
    details['high_bidask_mid'] = ae_consts.to_f(high_bid + high_ask / 2.0)
    details['mid_price'] = ae_consts.to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))
    details['nat_price'] = ae_consts.to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))

    cost_of_contracts_at_mid_price = None
    revenue_of_contracts_at_mid_price = None

    if trade_type == ae_consts.TRADE_ENTRY:
        cost_of_contracts_at_mid_price = ae_consts.to_f(
            100.0 * num_contracts * details['mid_price'])
        revenue_of_contracts_at_mid_price = ae_consts.to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == ae_consts.SPREAD_VERTICAL_BULL:
            if option_type == ae_consts.OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
        else:  # bear
            if option_type == ae_consts.OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price

    else:  # trade exit calculations:
        revenue_of_contracts_at_mid_price = ae_consts.to_f(
            100.0 * num_contracts * details['mid_price'])
        cost_of_contracts_at_mid_price = ae_consts.to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == ae_consts.SPREAD_VERTICAL_BULL:
            if option_type == ae_consts.OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
        else:  # bear
            if option_type == ae_consts.OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
    # end of supported types of spreads

    details['cost'] = cost_of_contracts_at_mid_price
    details['revenue'] = revenue_of_contracts_at_mid_price

    log.debug(
        f'type={ae_consts.get_status(status=trade_type)} '
        f'spread={ae_consts.get_status(status=spread_type)} '
        f'option={ae_consts.get_status(status=option_type)} '
        f'close={close} spread_id={details["spread_id"]} '
        f'revenue={revenue_of_contracts_at_mid_price} '
        f'cost={cost_of_contracts_at_mid_price} '
        f'mid={details["mid_price"]} width={details["strike_width"]} '
        f'max_profit={details["max_profit"]} max_loss={details["max_loss"]}')

    return details
# end of build_option_spread_details
