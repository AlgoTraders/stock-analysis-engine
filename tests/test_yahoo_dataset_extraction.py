"""
Test file for:
Yahoo Extract Data
"""

import mock
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ev
from analysis_engine.consts import get_status
from analysis_engine.build_result import build_result
from analysis_engine.api_requests \
    import get_ds_dict
from analysis_engine.api_requests \
    import build_cache_ready_pricing_dataset
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_pricing_dataset
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_yahoo_news_dataset
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_option_calls_dataset
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_option_puts_dataset
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


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
    sample_record = build_cache_ready_pricing_dataset(
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
    res = build_result(
        status=SUCCESS,
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
    sample_record = build_cache_ready_pricing_dataset(
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
    res = build_result(
        status=SUCCESS,
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
    sample_record = build_cache_ready_pricing_dataset(
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
    res = build_result(
        status=SUCCESS,
        err=None,
        rec=rec)
    return res
# end of mock_extract_options_from_redis_success


class TestYahooDatasetExtraction(BaseTestCase):
    """TestYahooDatasetExtraction"""

    def setUp(self):
        """setUp"""
        self.ticker = TICKER
    # end of setUp

    @mock.patch(
        (
            'analysis_engine.get_data_from_redis_key.'
            'get_data_from_redis_key'),
        new=mock_extract_pricing_from_redis_success)
    def test_extract_pricing_success(self):
        """test_extract_pricing_success"""
        test_name = 'test_extract_pricing_dataset_success'
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = extract_pricing_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            get_status(status=status),
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
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = extract_yahoo_news_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            get_status(status=status),
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
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = extract_option_calls_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            get_status(status=status),
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
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        status, df = extract_option_puts_dataset(
            work_dict=work)
        self.assertIsNotNone(
            df)
        self.assertEqual(
            get_status(status=status),
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
        if ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = get_ds_dict(
            ticker='NFLX',
            label='test_integration_extract_pricing')

        status, df = extract_pricing_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Option Puts are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_pricing

    def test_integration_extract_yahoo_news(self):
        """test_integration_extract_yahoo_news"""
        if ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = get_ds_dict(
            ticker='NFLX',
            label='test_integration_extract_news')

        status, df = extract_yahoo_news_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Option Puts are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_yahoo_news

    def test_integration_extract_option_calls(self):
        """test_integration_extract_option_calls"""
        if ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = get_ds_dict(
            ticker='NFLX',
            label='test_integration_extract_option_calls')

        status, df = extract_option_calls_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Option Calls are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_option_calls

    def test_integration_extract_option_puts(self):
        """test_integration_extract_option_puts"""
        if ev('INT_TESTS', '0') == '0':
            return

        # build dataset cache dictionary
        work = get_ds_dict(
            ticker='NFLX',
            label='test_integration_extract_option_puts')

        status, df = extract_option_puts_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                'Yahoo Option Puts are missing in redis '
                'for ticker={} status={}'.format(
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_option_puts

# end of TestYahooDatasetExtraction
