"""
Helper for determining the pricing for
an entry position on a bear put spread
"""

import analysis_engine.build_option_spread_details as spread_utils
from analysis_engine.consts import TRADE_ENTRY
from analysis_engine.consts import SPREAD_VERTICAL_BEAR
from analysis_engine.consts import OPTION_PUT
from analysis_engine.consts import get_status
from analysis_engine.consts import ppj
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def build_entry_put_spread_details(
        ticker,
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_entry_put_spread_details

    Calculate pricing information for
    buying into ``Vertical Bear Put Option Spread`` contracts

    :param ticker: string ticker symbol
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

    spread_details = spread_utils.build_option_spread_details(
        trade_type=TRADE_ENTRY,
        spread_type=SPREAD_VERTICAL_BEAR,
        option_type=OPTION_PUT,
        close=close,
        num_contracts=num_contracts,
        low_strike=low_strike,
        low_ask=low_ask,
        low_bid=low_bid,
        high_strike=high_strike,
        high_ask=high_ask,
        high_bid=high_bid)

    log.debug(
        '{} type={} spread={} option={} close={} spread={}'.format(
            ticker,
            get_status(status=spread_details['trade_type']),
            get_status(status=spread_details['spread_type']),
            get_status(status=spread_details['option_type']),
            close,
            ppj(spread_details)))

    return spread_details
# end of build_entry_put_spread_details
