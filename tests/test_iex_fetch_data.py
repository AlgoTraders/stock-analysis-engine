"""
Test file for:
IEX Fetch Data
"""

import mock
import analysis_engine.mocks.mock_iex as mock_iex
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import ev
from analysis_engine.iex.consts import FETCH_FINANCIALS
from analysis_engine.consts import FETCH_MODE_IEX
from analysis_engine.iex.fetch_data \
    import fetch_data
from analysis_engine.api_requests \
    import build_iex_fetch_minute_request
from analysis_engine.api_requests \
    import build_iex_fetch_daily_request
from analysis_engine.api_requests \
    import build_iex_fetch_quote_request
from analysis_engine.api_requests \
    import build_iex_fetch_stats_request
from analysis_engine.api_requests \
    import build_iex_fetch_peers_request
from analysis_engine.api_requests \
    import build_iex_fetch_news_request
from analysis_engine.api_requests \
    import build_iex_fetch_financials_request
from analysis_engine.api_requests \
    import build_iex_fetch_earnings_request
from analysis_engine.api_requests \
    import build_iex_fetch_dividends_request
from analysis_engine.api_requests \
    import build_iex_fetch_company_request
from analysis_engine.api_requests \
    import build_get_new_pricing_request
from analysis_engine.work_tasks.get_new_pricing_data \
    import get_new_pricing_data


class TestIEXFetchData(BaseTestCase):
    """TestIEXFetchData"""

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_daily)
    def test_fetch_daily(self):
        """test_fetch_daily"""
        test_name = 'test_fetch_daily'
        work = build_iex_fetch_daily_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_daily

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_minute)
    def test_fetch_minute(self):
        """test_fetch_minute"""
        test_name = 'test_fetch_minute'
        work = build_iex_fetch_minute_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_minute

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_quote)
    def test_fetch_quote(self):
        """test_fetch_quote"""
        work = build_iex_fetch_quote_request(
            label='test_fetch_quote')

        work['ticker'] = 'test_fetch_quote'

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
        self.assertEqual(
            res['testcase'][0],
            'mock-quote')
    # end of test_fetch_quote

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_stats)
    def test_fetch_stats(self):
        """test_fetch_stats"""
        test_name = 'test_fetch_stats'
        work = build_iex_fetch_stats_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_stats

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_peers)
    def test_fetch_peers(self):
        """test_fetch_peers"""
        test_name = 'test_fetch_peers'
        work = build_iex_fetch_peers_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_peers

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_news)
    def test_fetch_news(self):
        """test_fetch_news"""
        test_name = 'test_fetch_news'
        work = build_iex_fetch_news_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_news

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_financials)
    def test_fetch_financials(self):
        """test_fetch_financials"""
        test_name = 'test_fetch_financials'
        work = build_iex_fetch_financials_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_financials

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_earnings)
    def test_fetch_earnings(self):
        """test_fetch_earnings"""
        test_name = 'test_fetch_earnings'
        work = build_iex_fetch_earnings_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_earnings

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_dividends)
    def test_fetch_dividends(self):
        """test_fetch_dividends"""
        test_name = 'test_fetch_dividends'
        work = build_iex_fetch_dividends_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_dividends

    @mock.patch(
        ('analysis_engine.iex.helpers_for_iex_api.get_from_iex'),
        new=mock_iex.mock_company)
    def test_fetch_company(self):
        """test_fetch_company"""
        test_name = 'test_fetch_company'
        work = build_iex_fetch_company_request(
            label=test_name)

        work['ticker'] = test_name

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
    # end of test_fetch_company

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
        print(f'dataframe: {df}')
        print('')
        print(f'dataframe columns:\n{df.columns.values}')
        print('-----------------------------------')
    # end of debug_df

    def test_integration_fetch_daily(self):
        """test_integration_fetch_daily"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_daily_request(
            label='test_integration_fetch_daily')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_daily

    def test_integration_fetch_minute(self):
        """test_integration_fetch_minute"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_minute_request(
            label='test_integration_fetch_minute')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_minute

    def test_integration_fetch_quote(self):
        """test_integration_fetch_quote"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_quote_request(
            label='test_integration_fetch_quote')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_quote

    def test_integration_fetch_stats(self):
        """test_integration_fetch_stats"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_stats_request(
            label='test_integration_fetch_stats')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_stats

    def test_integration_fetch_peers(self):
        """test_integration_fetch_peers"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_peers_request(
            label='test_integration_fetch_peers')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_peers

    def test_integration_fetch_news(self):
        """test_integration_fetch_news"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_news_request(
            label='test_integration_fetch_news')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_news

    def test_integration_fetch_financials(self):
        """test_integration_fetch_financials"""
        if ev('INT_TESTS', '0') == '0':
            return

        label = 'test_integration_fetch_financials'

        # store data
        work = build_iex_fetch_financials_request(
            label=label)
        work['ticker'] = 'TSLA'

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_financials

    def test_integration_fetch_earnings(self):
        """test_integration_fetch_earnings"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_earnings_request(
            label='test_integration_fetch_earnings')
        work['ticker'] = 'AAPL'

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_earnings

    def test_integration_fetch_dividends(self):
        """test_integration_fetch_dividends"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_dividends_request(
            label='test_integration_fetch_dividends')
        work['ticker'] = 'AAPL'

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_dividends

    def test_integration_fetch_company(self):
        """test_integration_fetch_company"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_company_request(
            label='test_integration_fetch_company')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_fetch_company

    def test_integration_get_financials_helper(self):
        """test_integration_get_financials_helper

        After running, there should be an updated timestamp on
        the s3 key:

        ::

            testing_<TICKER>_financials

        View the financials bucket:

        ::

            aws --endpoint-url http://localhost:9000 s3 ls s3://financials

        View the redis cache using the redis-cli:

        ::

            ./tools/redis-cli.sh
            127.0.0.1:6379> keys testing_TSLA_financials
            1) "testing_TSLA_financials"

        """
        if ev('INT_TESTS', '0') == '0':
            return

        label = 'test_integration_get_financials_helper'

        # store data
        work = build_get_new_pricing_request(
            label=label)

        work['fetch_mode'] = FETCH_MODE_IEX
        work['iex_datasets'] = [
            FETCH_FINANCIALS
        ]
        work['ticker'] = 'AAPL'
        work['s3_bucket'] = 'testing'
        work['s3_key'] = f'testing_{work["ticker"]}'
        work['redis_key'] = f'testing_{work["ticker"]}'
        work['celery_disabled'] = True
        dataset_results = get_new_pricing_data(
            work)

        self.assertIsNotNone(
            dataset_results)
        self.assertIsNotNone(
            len(dataset_results['rec']['financials']) >= 5)
    # end of test_integration_get_financials_helper

# end of TestIEXFetchData
