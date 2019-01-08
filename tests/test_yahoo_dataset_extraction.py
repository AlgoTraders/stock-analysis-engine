"""
Test file for:
Yahoo Extract Data
"""

import mock
import json
import analysis_engine.consts as ae_consts
import analysis_engine.mocks.base_test as base_test
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.yahoo.extract_df_from_redis as yahoo_extract
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def mock_extract_pricing_from_redis_success(
        label,
        host,
        port,
        db,
        password,
        key,
        **kwargs):
    """mock_extract_pricing_from_redis_success

    :param label: test label
    :param address: test address
    :param db: test db
    :param key: test key
    :param kwargs: additional keyword args as a dictionary
    """
    sample_record = api_requests.build_cache_ready_pricing_dataset(
        label=(
            '{}.{}.{}.{}.{}.'
            'mock_extract_pricing_from_redis_success'.format(
                label,
                host,
                port,
                db,
                key)))
    rec = {
        'data': sample_record['pricing']
    }
    res = build_result.build_result(
        status=ae_consts.SUCCESS,
        err=None,
        rec=rec)
    return res
# end of mock_extract_pricing_from_redis_success


def mock_extract_news_from_redis_success(
        label,
        host,
        port,
        db,
        password,
        key,
        **kwargs):
    """mock_extract_news_from_redis_success

    :param label: test label
    :param address: test address
    :param db: test db
    :param key: test key
    :param kwargs: additional keyword args as a dictionary
    """
    sample_record = api_requests.build_cache_ready_pricing_dataset(
        label=(
            '{}.{}.{}.{}.{}.'
            'mock_extract_news_from_redis_success'.format(
                label,
                host,
                port,
                db,
                key)))
    rec = {
        'data': sample_record['news']
    }
    res = build_result.build_result(
        status=ae_consts.SUCCESS,
        err=None,
        rec=rec)
    return res
# end of mock_extract_news_from_redis_success


def mock_extract_options_from_redis_success(
        label,
        host,
        port,
        db,
        password,
        key,
        **kwargs):
    """mock_extract_options_from_redis_success

    :param label: test label
    :param address: test address
    :param db: test db
    :param key: test key
    :param kwargs: additional keyword args as a dictionary
    """
    sample_record = api_requests.build_cache_ready_pricing_dataset(
        label=(
            '{}.{}.{}.{}.{}.'
            'mock_extract_options_from_redis_success'.format(
                label,
                host,
                port,
                db,
                key)))
    options_dict = sample_record['options']
    rec = {
        'data': options_dict
    }
    res = build_result.build_result(
        status=ae_consts.SUCCESS,
        err=None,
        rec=rec)
    return res
# end of mock_extract_options_from_redis_success


class TestYahooDatasetExtraction(base_test.BaseTestCase):
    """TestYahooDatasetExtraction"""

    def setUp(self):
        """setUp"""
        self.ticker = ae_consts.TICKER
    # end of setUp

    @mock.patch(
        (
            'analysis_engine.get_data_from_redis_key.'
            'get_data_from_redis_key'),
        new=mock_extract_pricing_from_redis_success)
    def test_extract_pricing_success(self):
        """test_extract_pricing_success"""
        test_name = 'test_extract_pricing_dataset_success'
        work = api_requests.get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = yahoo_extract.extract_pricing_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            ae_consts.get_status(status=status),
            'SUCCESS')
        self.assertTrue(
            len(df.index) == 1)
        self.assertEqual(
            df['regularMarketPrice'][0],
            288.09)
    # end of test_extract_pricing_success

    @mock.patch(
        (
            'analysis_engine.get_data_from_redis_key.'
            'get_data_from_redis_key'),
        new=mock_extract_news_from_redis_success)
    def test_extract_news_success(self):
        """test_extract_news_success"""
        test_name = 'test_extract_news_success'
        work = api_requests.get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = yahoo_extract.extract_yahoo_news_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            ae_consts.get_status(status=status),
            'SUCCESS')
        self.assertTrue(
            len(df.index) == 2)
        self.assertEqual(
            df['u'][1],
            'http://finance.yahoo.com/news/url2')
        self.assertEqual(
            df['tt'][1],
            '1493311950')
    # end of test_extract_news_success

    @mock.patch(
        (
            'analysis_engine.get_data_from_redis_key.'
            'get_data_from_redis_key'),
        new=mock_extract_options_from_redis_success)
    def test_extract_option_calls_success(self):
        """test_extract_option_calls_success"""
        test_name = 'test_extract_option_calls_success'
        work = api_requests.get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = yahoo_extract.extract_option_calls_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            ae_consts.get_status(status=status),
            'SUCCESS')
        self.assertTrue(
            len(df.index) == 1)
        self.assertEqual(
            df['strike'][0],
            380)
    # end of test_extract_option_calls_success

    @mock.patch(
        (
            'analysis_engine.get_data_from_redis_key.'
            'get_data_from_redis_key'),
        new=mock_extract_options_from_redis_success)
    def test_extract_option_puts_success(self):
        """test_extract_option_puts_success"""
        test_name = 'test_extract_option_puts_success'
        work = api_requests.get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = yahoo_extract.extract_option_puts_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            ae_consts.get_status(status=status),
            'SUCCESS')
        self.assertTrue(
            len(df.index) == 1)
        self.assertEqual(
            df['strike'][0],
            380)
    # end of test_extract_option_puts_success

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

    def test_integration_extract_pricing(self):
        """test_integration_extract_pricing"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker='SPY',
            label='test_integration_extract_pricing')

        status, df = yahoo_extract.extract_pricing_dataset(
            work_dict=work)
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Pricing are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    ae_consts.get_status(status=status)))
    # end of test_integration_extract_pricing

    def test_integration_extract_yahoo_news(self):
        """test_integration_extract_yahoo_news"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker='SPY',
            label='test_integration_extract_news')

        status, df = yahoo_extract.extract_yahoo_news_dataset(
            work_dict=work)
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo News is missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    ae_consts.get_status(status=status)))
    # end of test_integration_extract_yahoo_news

    def test_integration_extract_option_calls(self):
        """test_integration_extract_option_calls"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker='SPY',
            base_key='SPY_2018-12-31',
            label='test_integration_extract_option_calls')

        status, df = yahoo_extract.extract_option_calls_dataset(
            work_dict=work)
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
            self.assertTrue(ae_consts.is_df(df=df))
            for i, r in df.iterrows():
                print(ae_consts.ppj(json.loads(r.to_json())))
            log.info(
                'done printing option call data')
        else:
            log.critical(
                'Yahoo Option Calls are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    ae_consts.get_status(status=status)))
    # end of test_integration_extract_option_calls

    def test_integration_extract_option_puts(self):
        """test_integration_extract_option_puts"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker='SPY',
            label='test_integration_extract_option_puts')

        status, df = yahoo_extract.extract_option_puts_dataset(
            work_dict=work)
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Option Puts are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    ae_consts.get_status(status=status)))
    # end of test_integration_extract_option_puts

# end of TestYahooDatasetExtraction
