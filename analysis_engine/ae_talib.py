"""
TA-Lib wrappers
"""

# for unittests, allow passing the mocks into the runtime if not found
try:
    import talib as ta
except Exception:
    import analysis_engine.mocks.mock_talib as ta
# end of loading talib or mocks
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


"""
Overlap

https://mrjbq7.github.io/ta-lib/func_groups/overlap_studies.html
"""


def BBANDS(
        close,
        timeperiod=5,
        nbdevup=2,
        nbdevdn=2,
        matype=0,
        verbose=False):
    """BBANDS

    Wrapper for ta.BBANDS for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        (upperband,
         middleband,
         lowerband) = BBANDS(
            close,
            timeperiod=5,
            nbdevup=2,
            nbdevdn=2,
            matype=0)

    :return: upperband, middleband, lowerband
    :param close: close prices
    :param timeperiod: number of values
        (default is ``5``)
    :param nbdevup: float - standard deviation
        to set the upper band
        (default is ``2``)
    :param nbdevdn: float - standard deviation
        to set the lower band
        (default is ``2``)
    :param matype: moving average type
        (default is ``0`` simple moving average)
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'bbands - start')
    return ta.BBANDS(
        close,
        timeperiod=timeperiod,
        nbdevup=nbdevup,
        nbdevdn=nbdevdn,
        matype=matype)
# end of BBANDS


def EMA(
        close,
        timeperiod=30,
        verbose=False):
    """EMA

    Wrapper for ta.EMA for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = EMA(
            close,
            timeperiod=30)

    :return: float
    :param close: close prices
    :param timeperiod: number of values
        (default is ``5``)
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'ema - start')
    return ta.EMA(
        close,
        timeperiod=timeperiod)
# end of EMA


def WMA(
        close,
        timeperiod=30,
        verbose=False):
    """WMA

    Wrapper for ta.WMA for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = WMA(
            close,
            timeperiod=30)

    :return: float
    :param close: close prices
    :param timeperiod: number of values
        (default is ``5``)
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'ema - start')
    return ta.WMA(
        close,
        timeperiod=timeperiod)
# end of WMA


"""
Momentum

https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html
"""


def ADX(
        high=None,
        low=None,
        close=None,
        timeperiod=14,
        verbose=False):
    """ADX

    Wrapper for ta.ADX for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = ADX(
            high,
            low,
            close,
            timeperiod=14)

    :param high: high list
    :param low: low list
    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'adx - start')
    return ta.ADX(
        high,
        low,
        close,
        timeperiod)
# end of ADX


def MACD(
        close=None,
        fast_period=12,
        slow_period=26,
        signal_period=9,
        verbose=False):
    """MACD

    Wrapper for ta.MACD for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        (macd,
         macdsignal,
         macdhist) = MACD(
            close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9)

    :param value: list of values
        (default ``closes``)
    :param fast_period: integer fast
        line
    :param slow_period: integer slow
        line
    :param signal_period: integer signal
        line
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'macd - start')
    return ta.MACD(
        close,
        fastperiod=fast_period,
        slowperiod=slow_period,
        signalperiod=signal_period)
# end of MACD


def MFI(
        high=None,
        low=None,
        close=None,
        volume=None,
        timeperiod=None,
        verbose=False):
    """MFI

    Wrapper for ta.MFI for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = MFI(
            high,
            low,
            close,
            volume,
            timeperiod=14)

    :param high: high list
    :param low: low list
    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'mfi - start')
    return ta.MFI(
        high,
        low,
        close,
        volume,
        timeperiod)
# end of MFI


def MOM(
        close=None,
        timeperiod=None,
        verbose=False):
    """MOM

    Wrapper for ta.MOM for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = MOM(
            close,
            timeperiod=10)

    :param high: high list
    :param low: low list
    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'mom - start')
    return ta.MOM(
        close,
        timeperiod)
# end of MOM


def ROC(
        close=None,
        timeperiod=None,
        verbose=False):
    """ROC

    Wrapper for ta.ROC for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = ROC(
            close,
            timeperiod=10)

    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'roc - start')
    return ta.ROC(
        close,
        timeperiod)
# end of ROC


def RSI(
        close=None,
        timeperiod=None,
        verbose=False):
    """RSI

    Wrapper for ta.RSI for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = RSI(
            close,
            timeperiod=14)

    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'rsi - start')
    return ta.RSI(
        close,
        timeperiod)
# end of RSI


def STOCH(
        high=None,
        low=None,
        close=None,
        fastk_period=None,
        slowk_period=None,
        slowk_matype=None,
        slowd_period=None,
        slowd_matype=0,
        verbose=False):
    """STOCH

    Wrapper for ta.STOCH for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        slowk, slowd = STOCH(
            high,
            low,
            close,
            fastk_period=5,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0)

    :param high: list of high values
    :param low: list of low values
    :param close: list of close values
    :param fastk_period: integer num
        of fast k sticks
    :param slowk_period: integer num
        of slow k sticks
    :param slowk_matype: integer moving
        average
        (default is ``0``)
    :param slowd_period: integer num
        of slow d sticks
    :param slowd_matype: integer moving
        average
        (default is ``0``)
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'stoch - start')
    return ta.STOCH(
        high=high,
        low=low,
        close=close,
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowk_matype=slowk_matype,
        slowd_period=slowd_period,
        slowd_matype=slowd_matype)
# end of STOCH


def STOCHF(
        high=None,
        low=None,
        close=None,
        fastk_period=None,
        fastd_period=None,
        fastd_matype=0,
        verbose=False):
    """STOCHF

    Wrapper for ta.STOCHF for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        fastk, fastd = STOCHF(
            high,
            low,
            close,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0)

    :param high: list of high values
    :param low: list of low values
    :param close: list of close values
    :param fastk_period: integer num
        of fast k sticks
    :param fastd_period: integer num
        of fast d sticks
    :param fastd_matype: integer moving
        average
        (default is ``0``)
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'stoch - start')
    return ta.STOCHF(
        high=high,
        low=low,
        close=close,
        fastk_period=fastk_period,
        fastd_period=fastd_period,
        fastd_matype=fastd_matype)
# end of STOCHF


def WILLR(
        high=None,
        low=None,
        close=None,
        timeperiod=None,
        verbose=False):
    """WILLR

    Wrapper for ta.WILLR for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = WILLR(
            high,
            low,
            close,
            timeperiod=14)

    :param high: high list
    :param low: low list
    :param close: close list
    :param timeperiod: number of values
        in ``high``, ``low`` and ``close``
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'willr - start')
    return ta.WILLR(
        high,
        low,
        close,
        timeperiod)
# end of WILLR


"""
Volume

https://mrjbq7.github.io/ta-lib/func_groups/volume_indicators.html
"""


def Chaikin(
        high=None,
        low=None,
        close=None,
        volume=None,
        verbose=False):
    """Chaikin

    Wrapper for ta.AD for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = AD(
            high,
            low,
            close,
            volume)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'chaikin - start')
    return ta.AD(
        high,
        low,
        close,
        volume)
# end of Chaikin


def ChaikinADOSC(
        high=None,
        low=None,
        close=None,
        volume=None,
        fast_period=3,
        slow_period=10,
        verbose=False):
    """ChaikinADOSC

    Wrapper for ta.ADOSC for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = ADOSC(
            high,
            low,
            close,
            volume,
            fastperiod=3,
            slowperiod=10)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'chaikinadosc - start')
    return ta.ADOSC(
        high,
        low,
        close,
        volume,
        fast_period,
        slow_period)
# end of ChaikinADOSC


def OBV(
        value=None,
        volume=None,
        verbose=False):
    """OBV

    Wrapper for ta.OBV for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = OBV(
            close,
            volume)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'obv - start')
    return ta.OBV(
        value,
        volume)
# end of OBV


"""
Volume

https://mrjbq7.github.io/ta-lib/func_groups/volatility_indicators.html
"""


def ATR(
        high=None,
        low=None,
        close=None,
        timeperiod=None,
        verbose=False):
    """ATR

    Wrapper for ta.ATR for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = ATR(
            high,
            low,
            close,
            timeperiod=14)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'atr - start')
    return ta.ATR(
        high,
        low,
        close,
        timeperiod=timeperiod)
# end of ATR


def NATR(
        high=None,
        low=None,
        close=None,
        timeperiod=None,
        verbose=False):
    """NATR

    Wrapper for ta.NATR for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = NATR(
            high,
            low,
            close,
            timeperiod=14)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'natr - start')
    return ta.NATR(
        high,
        low,
        close,
        timeperiod=timeperiod)
# end of NATR


def TRANGE(
        high=None,
        low=None,
        close=None,
        verbose=False):
    """TRANGE

    Wrapper for ta.TRANGE for running unittests
    on ci/cd tools that do not provide talib

    .. code-block:: python

        real = TRANGE(
            high,
            low,
            close)

    :param value: list of values
        (default should be ``close``)
    :param volume: list of volume values
    :param verbose: show logs
    """
    if verbose:
        log.info(
            'trange - start')
    return ta.TRANGE(
        high,
        low,
        close)
# end of TRANGE
