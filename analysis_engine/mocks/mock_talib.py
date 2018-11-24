"""
Mock TA-Lib objects
"""

import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def MockWILLR(
        high=None,
        low=None,
        close=None,
        timeperiod=None):
    """MockWILLR

    build a mock wiliams r object
    to test indicators without having talib installed

    :param high: list of highs
    :param low: list of lows
    :param close: list of closes
    :param timeperiod: integer number of values
        in ``high``, ``low`` and ``close``
    """
    log.info('mock - MockTALib.WILLR - set')
    retval = []
    for h in high:
        retval.append(None)
    retval[-1] = -88.9
    return retval
# end of MockWILLR
