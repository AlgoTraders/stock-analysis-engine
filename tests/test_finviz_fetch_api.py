"""
Test file for:
FinViz Fetch API
"""

import mock
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import ev
from analysis_engine.consts import get_status
from analysis_engine.finviz.fetch_api \
    import fetch_tickers_from_screener


class MockResponse:
    """MockResponse"""

    def __init__(
            self):
        self.text = None
        self.status_code = 200
    # end of __init__

# end of MockResponse


def mock_request_get(
        url):
    """mock_request_get_success

    :param url: url to test
    """
    res = MockResponse()

    if 'success' in url:
        res.status_code = 200
        res.text = (
            '<html><body>'
            '<table>'
            '<tbody>'
            '<tr>'
            '<td class="screener-body-table-nw">1</td>'
            '<td class="screener-body-table-nw">QS</td>'
            '<td class="screener-body-table-nw">Quant Solutions</td>'
            '<td class="screener-body-table-nw">Financial</td>'
            '<td class="screener-body-table-nw">Quant Engines</td>'
            '<td class="screener-body-table-nw">USA</td>'
            '<td class="screener-body-table-nw">1.1B</td>'     # mcap
            '<td class="screener-body-table-nw">30.01</td>'    # p/e
            '<td class="screener-body-table-nw">45.01</td>'    # prc
            '<td class="screener-body-table-nw">3.05%</td>'    # chg
            '<td class="screener-body-table-nw">177,777</td>'  # vol
            '</tr>'
            '<tr>'
            '<td class="screener-body-table-nw">2</td>'
            '<td class="screener-body-table-nw">SPY</td>'
            '<td class="screener-body-table-nw">Spyder</td>'
            '<td class="screener-body-table-nw">Financial</td>'
            '<td class="screener-body-table-nw">ETF</td>'
            '<td class="screener-body-table-nw">USA</td>'
            '<td class="screener-body-table-nw">-</td>'
            '<td class="screener-body-table-nw">-</td>'
            '<td class="screener-body-table-nw">280.40</td>'
            '<td class="screener-body-table-nw">2.05%</td>'
            '<td class="screener-body-table-nw">117,872,097</td>'
            '</tr>'
            '<tr>'
            '<td class="screener-body-table-nw">3</td>'
            '<td class="screener-body-table-nw">VXX</td>'
            '<td class="screener-body-table-nw">iPath S&P 500 VIX</td>'
            '<td class="screener-body-table-nw">Financial</td>'
            '<td class="screener-body-table-nw">ETF</td>'
            '<td class="screener-body-table-nw">USA</td>'
            '<td class="screener-body-table-nw">-</td>'
            '<td class="screener-body-table-nw">-</td>'
            '<td class="screener-body-table-nw">31.98</td>'
            '<td class="screener-body-table-nw">-7.33%</td>'
            '<td class="screener-body-table-nw">53,700,383</td>'
            '</tr>'
            '<tbody>'
            '</table>'
            '</body>'
            '</html>')
    elif 'empty' in url:
        res.status_code = 200
        res.text = (
            '<html><body>'
            '<table>'
            '<tr>'
            '</tr>'
            '</table>'
            '</body>'
            '</html>')
    elif 'failure' in url:
        res.status_code = 500
        res.text = (
            '<html><body>'
            'error'
            '</body>'
            '</html>')
    elif 'exception' in url:
        raise Exception(
            'mock_request_get - threw for url={}'.format(
                url))
    return res
# end of mock_request_get


class TestFinVizFetchAPI(BaseTestCase):
    """TestFinVizFetchAPI"""

    @mock.patch(
        ('requests.get'),
        new=mock_request_get)
    def test_fetch_tickers_from_screener_success(self):
        """test_fetch_tickers_from_screener_success"""
        url = (
            'success-'
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=an_recom_strongbuy,'
            'exch_nyse,fa_ltdebteq_low,fa_sales5years_o10&'
            'ft=4')
        res = fetch_tickers_from_screener(
            url=url)
        self.assertIsNotNone(
            res)
        self.assertTrue(
            len(res['rec']['data']) > 0)
        self.assertEqual(
            get_status(status=res['status']),
            'SUCCESS')
        self.assertEqual(
            res['rec']['data']['ticker'][0],
            'QS')
        self.assertEqual(
            res['rec']['data']['ticker'][1],
            'SPY')
        self.assertEqual(
            res['rec']['data']['ticker'][2],
            'VXX')
        self.assertEqual(
            res['rec']['tickers'][0],
            'QS')
        self.assertEqual(
            res['rec']['tickers'][1],
            'SPY')
        self.assertEqual(
            res['rec']['tickers'][2],
            'VXX')
    # end of test_fetch_tickers_from_screener_success

    @mock.patch(
        ('requests.get'),
        new=mock_request_get)
    def test_fetch_tickers_from_screener_empty_data(self):
        """test_fetch_tickers_from_screener_empty_data"""
        url = (
            'empty-'
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=an_recom_strongbuy,'
            'exch_nyse,fa_ltdebteq_low,fa_sales5years_o10&'
            'ft=4')
        res = fetch_tickers_from_screener(
            url=url)
        self.assertIsNotNone(
            res)
        self.assertTrue(
            len(res['rec']['data']) == 0)
        self.assertEqual(
            get_status(status=res['status']),
            'SUCCESS')
    # end of test_fetch_tickers_from_screener_empty_data

    @mock.patch(
        ('requests.get'),
        new=mock_request_get)
    def test_fetch_tickers_from_screener_failure_data(self):
        """test_fetch_tickers_from_screener_failure_data"""
        url = (
            'failure-'
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=an_recom_strongbuy,'
            'exch_nyse,fa_ltdebteq_low,fa_sales5years_o10&'
            'ft=4')
        res = fetch_tickers_from_screener(
            url=url)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            get_status(status=res['status']),
            'ERR')
        self.assertTrue(
            'finviz returned non-ok HTTP' in res['err'])
        self.assertIsNone(
            res['rec']['data'])
    # end of test_fetch_tickers_from_screener_failure_data

    @mock.patch(
        ('requests.get'),
        new=mock_request_get)
    def test_fetch_tickers_from_screener_exception(self):
        """test_fetch_tickers_from_screener_exception"""
        url = (
            'exception-'
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=an_recom_strongbuy,'
            'exch_nyse,fa_ltdebteq_low,fa_sales5years_o10&'
            'ft=4')
        res = fetch_tickers_from_screener(
            url=url)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            get_status(status=res['status']),
            'EX')
        self.assertIsNone(
            res['rec']['data'])
    # end of test_fetch_tickers_from_screener_exception

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

    def debug_df(
            self,
            df):
        """debug_df

        :param df: ``pandas.DataFrame`` from a fetch
        """
        print('-----------------------------------')
        print(
            'dataframe: {}'.format(
                df))
        print('')
        print(
            'dataframe columns:\n{}'.format(
                df.columns.values))
        print('-----------------------------------')
    # end of debug_df

    def test_integration_test_fetch_tickers_from_screener(self):
        """test_integration_test_fetch_tickers_from_screener"""
        if ev('INT_TESTS', '0') == '0':
            return

        default_url = (
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=an_recom_strongbuy,'
            'exch_nyse,fa_ltdebteq_low,fa_sales5years_o10&'
            'ft=4')
        url = ev('INT_TEST_FINVIZ_SCREEN_URL', default_url)
        res = fetch_tickers_from_screener(
            url=url)
        self.assertIsNotNone(
            res)
        self.assertTrue(
            len(res['rec']['data']) > 0)
        self.assertEqual(
            get_status(status=res['status']),
            'SUCCESS')
        self.debug_df(df=res['rec']['data'])
    # end of test_integration_test_fetch_tickers_from_screener

# end of TestFinVizFetchAPI
