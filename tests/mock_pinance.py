"""
Mock Pinance Object for unittests
"""

import os


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
    options_data = os.getenv(
        'TEST_OPTIONS',
        {
            'openInterest': 0,
            'contractSize': 'REGULAR',
            'change': 0.0,
            'lastTradeDate': 1493323145,
            'impliedVolatility': 0.2500075,
            'strike': 286.0,
            'bid': 0.0,
            'inTheMoney': False,
            'lastPrice': 0.28,
            'percentChange': 0.0,
            'contractSymbol': 'SPY170505C00015000',
            'expiration': 1493942400,
            'volume': 1106,
            'ask': 0.0,
            'currency': 'USD'
        })
    return [
        options_data
    ]
# end of mock_get_options


class MockPinance:
    """MockPinance"""

    def __init__(
            self,
            symbol='SPY'):
        """__init__

        :param symbol: ticker
        """

        self.symbol = symbol
        self.quotes_data = {
            'language': 'en-US',
            'region': 'US',
            'quoteType': 'ETF',
            'quoteSourceName': 'Delayed Quote',
            'currency': 'USD',
            'postMarketChangePercent': 0.06941398,
            'postMarketTime': 1536623987,
            'fiftyDayAverageChangePercent': 0.010071794,
            'sourceInterval': 15,
            'exchangeTimezoneName': 'America/New_York',
            'exchangeTimezoneShortName': 'EDT',
            'gmtOffSetMilliseconds': -14400000,
            'shortName': 'SPDR S&P 500',
            'exchange': 'PCX',
            'marketState': 'POSTPOST',
            'priceHint': 2,
            'regularMarketPreviousClose': 287.6,
            'ask': 0.0,
            'bidSize': 10,
            'askSize': 8,
            'messageBoardId': 'finmb_6160262',
            'fullExchangeName': 'NYSEArca',
            'longName': 'SPDR S&amp;P 500 ETF',
            'financialCurrency': 'USD',
            'averageDailyVolume3Month': 64572187,
            'postMarketPrice': 288.3,
            'postMarketChange': 0.19998169,
            'regularMarketChangePercent': 0.17037213,
            'regularMarketDayRange': '287.88 - 289.03',
            'bid': 0.0,
            'market': 'us_market',
            'regularMarketPrice': 288.09,
            'regularMarketTime': 1536609602,
            'regularMarketChange': 0.48999023,
            'regularMarketOpen': 288.74,
            'regularMarketDayHigh': 289.03,
            'regularMarketDayLow': 287.88,
            'regularMarketVolume': 50210903,
            'esgPopulated': False,
            'tradeable': True,
            'fiftyTwoWeekHighChangePercent': -0.012511119,
            'fiftyTwoWeekLow': 248.02,
            'fiftyTwoWeekHigh': 291.74,
            'twoHundredDayAverage': 274.66153,
            'twoHundredDayAverageChange': 13.428467,
            'twoHundredDayAverageChangePercent': 0.048890963,
            'sharesOutstanding': 944232000,
            'fiftyDayAverage': 285.21735,
            'fiftyDayAverageChange': 2.8726501,
            'marketCap': 272023797760,
            'averageDailyVolume10Day': 67116380,
            'fiftyTwoWeekLowChange': 40.069992,
            'fiftyTwoWeekLowChangePercent': 0.16155952,
            'fiftyTwoWeekRange': '248.02 - 291.74',
            'fiftyTwoWeekHighChange': -3.649994,
            'exchangeDataDelayedBy': 0,
            'ytdReturn': 9.84,
            'trailingThreeMonthReturns': 7.63,
            'trailingThreeMonthNavReturns': 7.71,
            'symbol': 'SPY'
        }
        self.news_env_values = os.getenv(
            'TEST_NEWS',
            None)
        self.news_data = [
            {
                'u': 'http://finance.yahoo.com/news/url1',
                'usg': 'ke1',
                'sru': 'http://news.google.com/news/url?values',
                's': 'Yahoo Finance',
                'tt': '1493311950',
                'sp': 'Some Title 1',
                'd': '16 hours ago',
                't': 'Some Title 1'
            },
            {
                'u': 'http://finance.yahoo.com/news/url2',
                'usg': 'key2',
                'sru': 'http://news.google.com/news/url?values',
                's': 'Yahoo Finance',
                'tt': '1493311950',
                'sp': 'Some Title 2',
                'd': '18 hours ago',
                't': 'Some Title 2'
            }
        ]

        self.options_data = os.getenv(
            'TEST_OPTIONS',
            {
                'openInterest': 0,
                'contractSize': 'REGULAR',
                'change': 0.0,
                'lastTradeDate': 1493323145,
                'impliedVolatility': 0.2500075,
                'strike': 286.0,
                'bid': 0.0,
                'inTheMoney': False,
                'lastPrice': 0.28,
                'percentChange': 0.0,
                'contractSymbol': 'SPY170505C00015000',
                'expiration': 1493942400,
                'volume': 1106,
                'ask': 0.0,
                'currency': 'USD'
            })
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
