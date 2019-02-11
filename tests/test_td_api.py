"""
Test file for:
Tradier Extract Data
"""

import json
import requests
import analysis_engine.consts as ae_consts
import analysis_engine.options_dates as opt_dates
import analysis_engine.url_helper as url_helper
import analysis_engine.td.consts as td_consts
import analysis_engine.api_requests as api_requests
import analysis_engine.mocks.base_test as base_test
import analysis_engine.td.fetch_data as td_fetch
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class TestTDAPI(base_test.BaseTestCase):
    """TestTDAPI"""

    def setUp(self):
        """setUp"""
        self.ticker = ae_consts.TICKER
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
        print(f'dataframe: {df}')
        print('')
        print(f'dataframe columns:\n{df.columns.values}')
        print('-----------------------------------')
    # end of debug_df

    def test_integration_account_credentials(self):
        """test_integration_account_credentials"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return
        headers = td_consts.get_auth_headers()
        session = requests.Session()
        session.headers = headers
        self.exp_date = opt_dates.option_expiration().strftime(
            ae_consts.COMMON_DATE_FORMAT)
        use_url = td_consts.TD_URLS['options'].format(
            self.ticker,
            self.exp_date)
        response = url_helper.url_helper(sess=session).get(
                use_url
            )
        self.assertEqual(
            response.status_code,
            200)
        self.assertTrue(
            len(json.loads(response.text)) > 0)
    # end of test_integration_account_credentials

    def test_integration_fetch_calls_dataset(self):
        """test_integration_fetch_calls_dataset"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return
        ticker = 'SPY'
        label = 'TD calls dataset'
        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = td_fetch.fetch_data(
            work_dict=work,
            fetch_type='tdcalls')
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                f'{label} is missing in redis '
                f'for ticker={work["ticker"]} '
                f'status={ae_consts.get_status(status=status)}')
    # end of test_integration_fetch_calls_dataset

    def test_integration_fetch_puts_dataset(self):
        """test_integration_fetch_puts_dataset"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return
        ticker = 'SPY'
        label = 'TD puts dataset'
        # build dataset cache dictionary
        work = api_requests.get_ds_dict(
            ticker=ticker,
            label=label)

        status, df = td_fetch.fetch_data(
            work_dict=work,
            fetch_type='tdputs')
        if status == ae_consts.SUCCESS:
            self.assertIsNotNone(
                df)
            self.debug_df(df=df)
        else:
            log.critical(
                f'{label} is missing in redis '
                f'for ticker={work["ticker"]} '
                f'status={ae_consts.get_status(status=status)}')
    # end of test_integration_fetch_puts_dataset

# end of TestTDAPI
