"""
Test file for:
IEX Extract Data
"""

from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ev
from analysis_engine.consts import get_status
from analysis_engine.api_requests \
    import get_ds_dict
from analysis_engine.iex.extract_df_from_redis \
    import extract_daily_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_minute_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_quote_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_stats_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_peers_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_news_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_financials_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_earnings_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_dividends_dataset
from analysis_engine.iex.extract_df_from_redis \
    import extract_company_dataset
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


class TestIEXDatasetExtraction(BaseTestCase):
    """TestIEXDatasetExtraction"""

    def setUp(self):
        """setUp"""
        self.ticker = TICKER
    # end of setUp

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

    def test_integration_extract_daily_dataset(self):
        """test_integration_extract_daily_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX daily dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_daily_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_daily_dataset

    def test_integration_extract_minute_dataset(self):
        """test_integration_extract_minute_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX minute dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_minute_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                f'{label} is missing in redis '
                f'for ticker={work["ticker"]} '
                f'status={get_status(status=status)}')
    # end of test_integration_extract_minute_dataset

    def test_integration_extract_quote_dataset(self):
        """test_integration_extract_quote_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX quote dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_quote_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_quote_dataset

    def test_integration_extract_stats_dataset(self):
        """test_integration_extract_stats_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX stats dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_stats_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_stats_dataset

    def test_integration_extract_peers_dataset(self):
        """test_integration_extract_peers_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX peers dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_peers_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_peers_dataset

    def test_integration_extract_news_dataset(self):
        """test_integration_extract_news_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX news dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_news_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_news_dataset

    def test_integration_extract_financials_dataset(self):
        """test_integration_extract_financials_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX financials dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_financials_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_financials_dataset

    def test_integration_extract_earnings_dataset(self):
        """test_integration_extract_earnings_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX earnings dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_earnings_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_earnings_dataset

    def test_integration_extract_dividends_dataset(self):
        """test_integration_extract_dividends_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX dividends dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_dividends_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_dividends_dataset

    def test_integration_extract_company_dataset(self):
        """test_integration_extract_company_dataset"""
        if ev('INT_TESTS', '0') == '0':
            return
        ticker = 'NFLX'
        label = 'IEX company dataset'
        # build dataset cache dictionary
        work = get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = extract_company_dataset(
            work_dict=work)
        if status == SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                '{} is missing in redis '
                'for ticker={} status={}'.format(
                    label,
                    work['ticker'],
                    get_status(status=status)))
    # end of test_integration_extract_company_dataset

# end of TestIEXDatasetExtraction
