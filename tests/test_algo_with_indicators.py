"""
Test file for classes and functions:

- analysis_engine.algo.BaseAlgo
- analysis_engine.indicators.indicator_processor
- analysis_engine.indicators.build_indicator_node
- analysis_engine.indicators.base_indicator
- analysis_engine.indicators.load_indicator_from_module
- analysis_engine.build_algo_request
- analysis_engine.build_buy_order
- analysis_engine.build_sell_order
- analysis_engine.build_trade_history_entry

"""

import pandas as pd
import json
import mock
import analysis_engine.mocks.mock_talib as mock_talib
import analysis_engine.mocks.base_test as base_test
import analysis_engine.utils as ae_utils
import analysis_engine.utils as ae_consts
import analysis_engine.algo as base_algo


def mock_write_to_file(
        output_file,
        data):
    print(
        'mock - mock_write_to_file('
        'output_file={}, data={})'.format(
            output_file,
            len(data)))
    return True
# end of mock_write_to_file


def mock_write_to_file_failed(
        output_file,
        data):
    print(
        'mock - fail - mock_write_to_file('
        'output_file={}, data={})'.format(
            output_file,
            len(data)))
    return False
# end of mock_write_to_file_failed


class TestAlgoWithIndicators(base_test.BaseTestCase):
    """TestAlgoWithIndicators"""

    ticker = None
    last_close_str = None

    def setUp(
            self):
        """setUp"""
        self.ticker = 'SPY'
        self.daily_dataset = json.loads(
            open('tests/datasets/spy-daily.json', 'r').read())
        self.daily_df = pd.DataFrame(self.daily_dataset)
        self.daily_df['date'] = pd.to_datetime(
            self.daily_df['date'])
        self.start_date_str = self.daily_df['date'].iloc[0].strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        self.end_date_str = self.daily_df['date'].iloc[-1].strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        self.minute_df = pd.DataFrame([])
        self.options_df = pd.DataFrame([])
        self.use_date = '2018-11-05'
        self.dataset_id = '{}_{}'.format(
            self.ticker,
            self.use_date)
        self.datasets = [
            'daily'
        ]
        self.data = {}
        self.data[self.ticker] = [
            {
                'id': self.dataset_id,
                'date': self.use_date,
                'data': {
                    'daily': self.daily_df,
                    'minute': self.minute_df,
                    'options': self.options_df
                }
            }
        ]
        self.balance = 10000.00
        self.last_close_str = ae_utils.get_last_close_str(
            fmt=ae_consts.COMMON_DATE_FORMAT)
        self.output_dir = (
            '/opt/sa/tests/datasets/algo')

        self.example_indicator_path = (
            'analysis_engine/mocks/example_indicator_williamsr.py')
        self.algo_config_dict = {
            'name': 'test_5_days_ahead',
            'algo_module_path': None,
            'algo_version': 1,
            'trade_horizon_units': 'day',
            'trade_horizon': 5,
            'buy_rules': {
                'confidence': 75,
                'min_indicators': 1
            },
            'sell_rules': {
                'confidence': 75,
                'min_indicators': 1
            },
            'indicators': [
                {
                    'name': 'willr',
                    'module_path': self.example_indicator_path,
                    'category': 'technical',
                    'type': 'momentum',
                    'uses_data': 'daily',
                    'high': 0,
                    'low': 0,
                    'open': 0,
                    'willr_value': 0,
                    'num_points': 12,
                    'buy_above': 60,
                    'sell_below': 20
                }
            ],
            'slack': {
                'webhook': None
            }
        }

    # end of setUp

    @mock.patch(
        ('analysis_engine.talib.WILLR'),
        new=mock_talib.WILLR)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily_indicator_with_algo_config(self):
        """test_run_daily_indicator_with_algo_config"""
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=self.balance,
            start_date_str=self.start_date_str,
            end_date_str=self.end_date_str,
            config_dict=self.algo_config_dict)
        self.assertEqual(
            algo.name,
            self.algo_config_dict['name'])
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        algo.handle_data(
            data=self.data)
    # end of test_run_daily_indicator_with_algo_config

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

# end of TestAlgoWithIndicators
