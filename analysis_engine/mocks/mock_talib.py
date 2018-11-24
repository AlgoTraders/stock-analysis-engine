"""
Mock TA-Lib objects
"""

import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def WILLR(
        high=None,
        low=None,
        close=None,
        timeperiod=None):
    """WILLR

    build a mock wiliams r object
    to test indicators using the talib

    :param high: hostname
    :param low: port
    :param close: password
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    """
    log.info('mock - MockTALib.WILLR - set')
    retval = []
    for h in high:
        retval.append(None)
    retval[-1] = -88.9
    return retval
# end of WILLR
