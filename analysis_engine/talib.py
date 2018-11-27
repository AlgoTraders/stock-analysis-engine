"""
TA-Lib wrappers
"""

# for unittests, allow passing the mocks into the runtime if not found
try:
    import talib
except Exception:
    import analysis_engine.mocks.mock_talib as talib
# end of loading talib or mocks
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def WILLR(
        high=None,
        low=None,
        close=None,
        timeperiod=None,
        verbose=False):
    """WILLR

    Wrapper for talib.WILLR for running unittests
    on ci/cd tools that do not provide talib

    :param high: hostname
    :param low: port
    :param close: password
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'willr - start')
    return talib.WILLR(
        high,
        low,
        close,
        timeperiod)
# end of WILLR
