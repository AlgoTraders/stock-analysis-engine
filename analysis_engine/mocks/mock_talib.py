"""
Mock TA-Lib objects
"""

import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def MockWILLRBuy(
        high=None,
        low=None,
        close=None,
        timeperiod=None):
    """MockWILLRBuy

    build a mock wiliams r object that will report
    an ``buy`` value to test indicators without
    having talib installed

    :param high: list of highs
    :param low: list of lows
    :param close: list of closes
    :param timeperiod: integer number of values
        in ``high``, ``low`` and ``close``
    """
    log.warn('mock - MockTALib.WILLR - BUY')
    retval = []
    for h in high:
        retval.append(None)
    retval[-1] = -99.9
    return retval
# end of MockWILLRBuy


def MockWILLRSell(
        high=None,
        low=None,
        close=None,
        timeperiod=None):
    """MockWILLRSell

    build a mock wiliams r object that will report
    an ``sell`` value to test indicators without
    having talib installed

    :param high: list of highs
    :param low: list of lows
    :param close: list of closes
    :param timeperiod: integer number of values
        in ``high``, ``low`` and ``close``
    """
    log.warn('mock - MockTALib.WILLR - SELL')
    retval = []
    for h in high:
        retval.append(None)
    retval[-1] = -1.0
    return retval
# end of MockWILLRSell


def MockWILLRIgnore(
        high=None,
        low=None,
        close=None,
        timeperiod=None):
    """MockWILLRIgnore

    build a mock wiliams r object that will report
    an ``ignore`` value to test indicators without
    having talib installed

    :param high: list of highs
    :param low: list of lows
    :param close: list of closes
    :param timeperiod: integer number of values
        in ``high``, ``low`` and ``close``
    """
    log.warn('mock - MockTALib.WILLR - IGNORE')
    retval = []
    for h in high:
        retval.append(None)
    retval[-1] = -50.0
    return retval
# end of MockWILLRIgnore
