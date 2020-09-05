"""
Test file for:
algo_runner.py
"""

import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.algo_runner as algo_runner
import analysis_engine.mocks.base_test as base_test
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class TestRunnerForAlgos(base_test.BaseTestCase):
    """TestRunnerForAlgos"""

    def setUp(self):
        """setUp"""
        self.ticker = ae_consts.TICKER
        self.algo_config = (
            './cfg/default_algo.json')
        self.algo_history_loc = (
            f's3://ztestalgos/test_history_{self.ticker}')
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

    def test_latest(self):
        """test_latest"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return
        ticker = 'SPY'
        start_date = ae_utils.get_last_close_str()
        # build dataset cache dictionary
        runner = algo_runner.AlgoRunner(
            ticker=ticker,
            start_date=start_date,
            end_date=None,
            history_loc=self.algo_history_loc,
            algo_config=self.algo_config,
            verbose_algo=True,
            verbose_processor=False,
            verbose_indicators=False)

        req = {
            'ticker': ticker,
            'date_str': start_date,
            'start_row': -200
        }
        df = runner.latest(
            **req)
        self.assertEqual(
            len(df.index),
            len(runner.get_history().index))
    # end of test_latest

# end of TestRunnerForAlgos
