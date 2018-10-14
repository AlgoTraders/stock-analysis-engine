"""
Test file for:
Yahoo Extract Data
"""

from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import TICKER
from analysis_engine.consts import ev
from analysis_engine.api_requests \
    import get_ds_dict
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_option_calls_dataset
from analysis_engine.yahoo.extract_df_from_redis \
    import extract_option_puts_dataset


class TestYahooDatasetExtraction(BaseTestCase):
    """TestYahooDatasetExtraction"""

    def setUp(self):
        """setUp"""
        self.ticker = TICKER
    # end of setUp

    def test_extract_option_calls(self):
        """test_extract_option_calls"""
        return
        test_name = 'test_extract_option_calls'
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        work['ticker'] = test_name
        work['timeframe'] = '{}_daily'.format(
            test_name)

        res = extract_option_calls_dataset(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
        self.assertEqual(
            res['timeframe'][0],
            work['timeframe'])
    # end of test_extract_option_calls

    def test_extract_option_puts(self):
        """test_extract_option_puts"""
        return
        test_name = 'test_extract_option_puts'
        work = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        work['ticker'] = test_name
        work['timeframe'] = '{}_minute'.format(
            test_name)

        res = extract_option_puts_dataset(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.assertEqual(
            res['symbol'][0],
            work['ticker'])
        self.assertEqual(
            res['timeframe'][0],
            work['timeframe'])
    # end of test_extract_option_puts

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

    def test_integration_extract_option_calls(self):
        """test_integration_extract_option_calls"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = get_ds_dict(
            ticker=self.ticker,
            label='test_integration_extract_option_calls')

        res = extract_option_calls_dataset(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_extract_option_calls

    def test_integration_extract_option_puts(self):
        """test_integration_extract_option_puts"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = get_ds_dict(
            ticker=self.ticker,
            label='test_integration_extract_option_puts')

        res = extract_option_puts_dataset(
            work_dict=work)
        self.assertIsNotNone(
            res)
        self.debug_df(df=res)
    # end of test_integration_extract_option_puts

# end of TestYahooDatasetExtraction
