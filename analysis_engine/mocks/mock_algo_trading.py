"""
Mock Algorithm Methods for unittesting things
like previously-owned shares or sell-side indicators
without owning shares
"""

import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def mock_algo_owns_shares_in_ticker_before_starting(
        obj,
        ticker):
    """mock_algo_owns_shares_in_ticker_before_starting

    Support mocking owned shares to test indicator selling

    If you can modify your algorithm ``config_dict`` you can
    also set a ``positions`` dictionary like:

    .. code-block:: python

        algo_config_dict = {
            # other values omitted for docs
            'positions': {
                'SPY': {
                    'shares': 10000,
                    'buys': [],
                    'sells': []
                }
            }
        }


    Use with your custom algorithm unittests:

    .. code-block:: python

        import mock
        import analysis_engine.mocks.mock_algo_trading as mock_trading

        @mock.patch(
            ('analysis_engine.algo.BaseAlgo.get_ticker_positions'),
            new=mock_trading.mock_algo_owns_shares_in_ticker_before_starting)


    :param obj: algorithm object
    :param ticker: ticker symbol
    """
    num_owned = 10000
    buys = []
    sells = []
    return num_owned, buys, sells
# end of mock_algo_owns_shares_in_ticker_before_starting
