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
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
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

        self.willr_close_path = (
            'analysis_engine/mocks/example_indicator_williamsr.py')
        self.willr_open_path = (
            'analysis_engine/mocks/example_indicator_williamsr_open.py')
        self.algo_config_dict = {
            'name': 'test_5_days_ahead',
            'algo_module_path': None,
            'algo_version': 1,
            'trade_horizon_units': 'day',
            'trade_horizon': 5,
            'num_owned': 10,
            'buy_shares': 10,
            'balance': 100000,
            'ticker': 'SPY',
            'positions': {
                'SPY': {
                    'shares': 10,
                    'buys': [],
                    'sells': []
                }
            },
            'buy_rules': {
                'confidence': 75,
                'min_indicators': 3
            },
            'sell_rules': {
                'confidence': 75,
                'min_indicators': 3
            },
            'indicators': [
                {
                    'name': 'willr_-70_-30',
                    'module_path': self.willr_close_path,
                    'category': 'technical',
                    'type': 'momentum',
                    'uses_data': 'daily',
                    'high': 0,
                    'low': 0,
                    'close': 0,
                    'open': 0,
                    'willr_value': 0,
                    'num_points': 10,
                    'buy_below': -70,
                    'sell_above': -30,
                    'is_buy': False,
                    'is_sell': False,
                    'verbose': True
                },
                {
                    'name': 'willr_-80_-20',
                    'module_path': self.willr_close_path,
                    'category': 'technical',
                    'type': 'momentum',
                    'uses_data': 'daily',
                    'high': 0,
                    'low': 0,
                    'close': 0,
                    'open': 0,
                    'willr_value': 0,
                    'num_points': 10,
                    'buy_below': -80,
                    'sell_above': -20,
                    'is_buy': False,
                    'is_sell': False
                },
                {
                    'name': 'willr_-90_-10',
                    'module_path': self.willr_close_path,
                    'category': 'technical',
                    'type': 'momentum',
                    'uses_data': 'daily',
                    'high': 0,
                    'low': 0,
                    'close': 0,
                    'open': 0,
                    'willr_value': 0,
                    'num_points': 10,
                    'buy_below': -90,
                    'sell_above': -10,
                    'is_buy': False,
                    'is_sell': False
                },
                {
                    'name': 'willr_open_-80_-20',
                    'module_path': self.willr_open_path,
                    'category': 'technical',
                    'type': 'momentum',
                    'uses_data': 'daily',
                    'high': 0,
                    'low': 0,
                    'close': 0,
                    'open': 0,
                    'willr_open_value': 0,
                    'num_points': 15,
                    'buy_below': -80,
                    'sell_above': -20,
                    'is_buy': False,
                    'is_sell': False
                }
            ],
            'slack': {
                'webhook': None
            }
        }

    # end of setUp

    @mock.patch(
        ('analysis_engine.talib.WILLR'),
        new=mock_talib.MockWILLRBuy)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily_indicator_with_algo_config_buy(self):
        """test_run_daily_indicator_with_algo_config_buy"""
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

        res = algo.get_result()
        print(ae_consts.ppj(res))
        self.assertTrue(
            len(res['history'][0]['total_sells']) == 0)
        self.assertTrue(
            len(res['history'][0]['total_buys']) == 1)
    # end of test_run_daily_indicator_with_algo_config_buy

    @mock.patch(
        ('analysis_engine.talib.WILLR'),
        new=mock_talib.MockWILLRSell)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily_indicator_with_algo_config_sell(self):
        """test_run_daily_indicator_with_algo_config_sell"""
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

        res = algo.get_result()
        print(ae_consts.ppj(res))
        self.assertTrue(
            len(res['history'][0]['total_sells']) == 1)
        self.assertTrue(
            len(res['history'][0]['total_buys']) == 0)
    # end of test_run_daily_indicator_with_algo_config_sell

    @mock.patch(
        ('analysis_engine.talib.WILLR'),
        new=mock_talib.MockWILLRIgnore)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily_indicator_with_algo_config_ignore(self):
        """test_run_daily_indicator_with_algo_config_ignore"""
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

        res = algo.get_result()
        print(ae_consts.ppj(res))
        self.assertTrue(
            len(res['history'][0]['total_sells']) == 0)
        self.assertTrue(
            len(res['history'][0]['total_buys']) == 0)
    # end of test_run_daily_indicator_with_algo_config_ignore

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_integration_daily_indicator_with_algo_config(self):
        """test_integration_daily_indicator_with_algo_config"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

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

        res = algo.get_result()
        print(ae_consts.ppj(res))
        self.assertTrue(
            len(res['history'][0]['total_sells']) == 0)
        self.assertTrue(
            len(res['history'][0]['total_buys']) == 0)
    # end of test_integration_daily_indicator_with_algo_config

# end of TestAlgoWithIndicators
