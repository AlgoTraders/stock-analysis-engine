"""
Mock Pinance Object for unittests
"""

import os
import analysis_engine.api_requests as api_requests


def mock_get_options(
        ticker=None,
        contract_type=None,
        exp_date_str=None,
        strike=None):
    """mock_get_options

    :param ticker: ticker to lookup
    :param exp_date_str: ``YYYY-MM-DD`` expiration date format
    :param strike: optional strike price, ``None`` returns
                    all option chains
    :param contract_type: ``C`` calls or ``P`` for puts, if
                            ``strike=None`` then the ``contract_type``
                            is ignored
    """
    mock_cache_data = api_requests.build_cache_ready_pricing_dataset(
        label='ticker')
    options_data = os.getenv(
        'TEST_OPTIONS',
        mock_cache_data['options'])
    return options_data
# end of mock_get_options


class MockPinance:
    """MockPinance"""

    def __init__(
            self,
            symbol='SPY'):
        """__init__

        :param symbol: ticker
        """

        mock_cache_data = api_requests.build_cache_ready_pricing_dataset(
            label='ticker')
        self.symbol = symbol
        self.quotes_data = mock_cache_data['pricing']
        self.news_data = mock_cache_data['news']
        self.options_data = mock_cache_data['options']
    # end of __init__

    def get_quotes(
            self):
        """get_quotes"""
        return self.quotes_data
    # end of get_quotes

    def get_news(
            self):
        """get_news"""
        return self.news_data
    # end of get_news

    def get_options(
            self,
            ticker=None,
            contract_type=None,
            exp_date_str=None,
            strike=None):
        """get_options

        :param ticker: ticker to lookup
        :param exp_date_str: ``YYYY-MM-DD`` expiration date format
        :param strike: optional strike price, ``None`` returns
                       all option chains
        :param contract_type: ``C`` calls or ``P`` for puts, if
                              ``strike=None`` then the ``contract_type``
                              is ignored
        """
        return [
            self.options_data
        ]
    # end of get_options

# end of MockPinance
