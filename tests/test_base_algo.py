"""
Test file for classes and functions:

- analysis_engine.algo.base_algo.BaseAlgo
- analysis_engine.run_algo.run_algo
- analysis_engine.build_algo_request
- analysis_engine.build_buy_order
- analysis_engine.build_sell_order
- analysis_engine.build_trade_history_entry

"""

import os
import uuid
import glob
import datetime
import pandas as pd
import mock
import types as use_types
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.show_dataset as show_dataset
import analysis_engine.mocks.mock_talib as mock_talib
import analysis_engine.algo as base_algo
import analysis_engine.run_algo as run_algo
import analysis_engine.mocks.mock_boto3_s3 as mock_s3
import analysis_engine.mocks.mock_redis as mock_redis
import analysis_engine.mocks.base_test as base_test
import analysis_engine.build_algo_request as build_algo_request
import analysis_engine.build_buy_order as build_buy_order
import analysis_engine.build_sell_order as build_sell_order
import analysis_engine.build_trade_history_entry as build_trade_history_entry
import analysis_engine.build_publish_request as build_publish_request
import analysis_engine.get_data_from_redis_key as redis_get


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


def mock_request_success_result(
        url,
        data):
    """mock_request_success_result

    Mock slack post_success

    :param kwargs: keyword args dict
    """
    res = {'status_code': 200}
    return use_types.SimpleNamespace(**res)
# end of mock_request_success_result


class TestBaseAlgo(base_test.BaseTestCase):
    """TestBaseAlgo"""

    ticker = None
    last_close_str = None

    def setUp(
            self):
        """setUp"""
        self.ticker = 'SPY'
        self.timeseries = 'day'
        self.trade_strategy = 'count'
        self.start_date_str = (
            '2018-11-01 15:59:59'  # Thursday
        )
        self.end_date_str = (
            '2018-11-05 15:59:59'  # Monday
        )
        self.use_end_date = datetime.datetime.now()
        self.use_end_date_str = self.use_end_date.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        self.use_start_date = (
            datetime.datetime.now() - datetime.timedelta(days=3))
        self.use_start_date_str = self.use_start_date.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        self.daily_df = pd.DataFrame([
            {
                'high': 280.01,
                'low': 270.01,
                'open': 275.01,
                'close': 272.02,
                'volume': 123,
                'date': self.start_date_str  # Thursday
            },
            {
                'high': 281.01,
                'low': 271.01,
                'open': 276.01,
                'close': 273.02,
                'volume': 125,
                'date': '2018-11-02 15:59:59'  # Friday
            },
            {
                'high': 282.01,
                'low': 272.01,
                'open': 277.01,
                'close': 274.02,
                'volume': 121,
                'date': self.end_date_str  # Monday
            }
        ])
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
            'verbose': True,
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
                    'num_points': 12,
                    'buy_above': 60,
                    'sell_below': 20,
                    'verbose': True
                }
            ],
            'slack': {
                'webhook': None
            }
        }

    # end of setUp

    def validate_dataset_structure(
            self,
            cur_algo):
        """validate_dataset_structure

        validate an algo's ``self.loaded_dataset`` has a valid structure

        :param cur_algo: ``analysis_engine.algo.BaseAlgo`` object
        """
        self.assertTrue(
            self.ticker in cur_algo.loaded_dataset)
        self.assertTrue(
            'id' in cur_algo.loaded_dataset[self.ticker][0])
        self.assertTrue(
            'date' in cur_algo.loaded_dataset[self.ticker][0])
        self.assertTrue(
            'data' in cur_algo.loaded_dataset[self.ticker][0])

        expected_datasets = ae_consts.DEFAULT_SERIALIZED_DATASETS
        loaded_ds = cur_algo.loaded_dataset[self.ticker]
        show_dataset.show_dataset(
            algo_dataset=cur_algo.loaded_dataset)
        """
        print(
            'testing: {} in node={}'.format(
                self.ticker,
                loaded_ds))
        """
        idx = 0
        for ds_node in loaded_ds:
            # print(str(ds_node)[0:40])
            self.assertTrue(
                'id' in ds_node)
            self.assertTrue(
                'date' in ds_node)
            self.assertTrue(
                'data' in ds_node)
            ds_data = ds_node['data']
            for ds_key in expected_datasets:
                """
                print(
                    'checking {} is in cur_algo.load'
                    'ed_dataset[{}][{}][\'data\']'.format(
                        ds_key,
                        self.ticker,
                        idx))
                """
                if ds_key not in [
                            'tdcalls',
                            'tdputs'
                        ]:
                    self.assertTrue(
                        ds_key in ds_data)
                    self.assertTrue(
                        hasattr(
                            ds_data[ds_key],
                            'empty'))
                    self.assertTrue(
                        hasattr(
                            ds_data[ds_key],
                            'to_json'))
                    self.assertTrue(
                        hasattr(
                            ds_data[ds_key],
                            'index'))
            # for all keys make sure the required fields exist
            idx += 1
        # for all ordered dataset nodes
    # end of validate_dataset_structure

    def test_build_algo_request_daily(self):
        """test_build_algo_request_daily"""
        use_key = 'test_build_algo_request_daily'
        req = build_algo_request.build_algo_request(
            ticker=self.ticker,
            use_key=use_key,
            start_date=self.start_date_str,
            end_date=self.end_date_str,
            datasets=self.datasets,
            balance=self.balance,
            label=use_key)
        self.assertEqual(
            req['tickers'],
            [self.ticker])
        self.assertEqual(
            req['extract_datasets'],
            [
                'SPY_2018-11-01',
                'SPY_2018-11-02',
                'SPY_2018-11-05'
            ])
    # end of test_build_algo_request_daily

    def test_build_algo_request_daily_with_config(self):
        """test_build_algo_request_daily_with_config"""
        use_key = 'test_build_algo_request_daily_with_config'
        req = build_algo_request.build_algo_request(
            ticker=self.ticker,
            use_key=use_key,
            start_date=self.start_date_str,
            end_date=self.end_date_str,
            datasets=self.datasets,
            balance=self.balance,
            config_file='not-real',
            config_dict=self.algo_config_dict,
            label=use_key)
        self.assertEqual(
            req['tickers'],
            [self.ticker])
        self.assertEqual(
            req['config_file'],
            'not-real')
        self.assertEqual(
            req['extract_datasets'],
            [
                'SPY_2018-11-01',
                'SPY_2018-11-02',
                'SPY_2018-11-05'
            ])
    # end of test_build_algo_request_daily_with_config

    def test_build_buy_order(self):
        """test_build_buy_order"""
        use_key = 'test_build_buy_order'
        date = '2018-11-02'
        close = 280.00
        buy_num = 5
        use_balance = self.balance
        expected_buy_price = 1412.00
        expected_balance = use_balance - expected_buy_price
        expected_prev_shares = 10
        expected_num_shares = expected_prev_shares + buy_num
        commission = 12.0
        details = {
            'test': use_key
        }
        req = build_buy_order.build_buy_order(
            ticker=self.ticker,
            close=close,            # 280.00
            balance=use_balance,    # 10000.00
            commission=commission,  # 12 to buy and 12 to sell
            details=details,
            date=date,
            num_owned=expected_prev_shares,  # currently owned shares
            shares=buy_num,  # buy 5 shares for (5 * 280) + 12 = 1412.00
            use_key=use_key,
            reason='testing {}'.format(use_key))
        print(ae_consts.ppj(req))
        self.assertEqual(
            ae_consts.get_status(status=req['status']),
            'TRADE_FILLED')
        self.assertEqual(
            req['ticker'],
            self.ticker)
        self.assertEqual(
            req['close'],
            close)
        self.assertEqual(
            req['buy_price'],
            expected_buy_price)
        self.assertEqual(
            req['prev_shares'],
            expected_prev_shares)
        self.assertEqual(
            req['prev_balance'],
            self.balance)
        self.assertEqual(
            req['shares'],
            expected_num_shares)
        self.assertEqual(
            req['balance'],
            expected_balance)
        self.assertEqual(
            req['details'],
            details)
    # end of test_build_buy_order

    def test_build_buy_order_not_enough_funds(self):
        """test_build_buy_order_not_enough_funds"""
        use_key = 'test_build_buy_order_not_enough_funds'
        date = '2018-11-02'
        close = 280.00
        buy_num = 5
        use_balance = 1411.00
        expected_buy_price = 1412.00
        expected_balance = use_balance - 0
        expected_prev_shares = 10
        expected_num_shares = expected_prev_shares
        commission = 12.0
        details = {
            'test': use_key
        }
        req = build_buy_order.build_buy_order(
            ticker=self.ticker,
            close=close,            # 280.00
            balance=use_balance,    # 1411.00
            commission=commission,  # 12 to buy and 12 to sell
            details=details,
            date=date,
            num_owned=expected_prev_shares,  # currently owned shares
            shares=buy_num,  # buy 5 shares for (5 * 280) + 12 = 1412.00
            use_key=use_key,
            reason='testing {}'.format(use_key))
        print(ae_consts.ppj(req))
        self.assertEqual(
            ae_consts.get_status(status=req['status']),
            'TRADE_NOT_ENOUGH_FUNDS')
        self.assertEqual(
            req['ticker'],
            self.ticker)
        self.assertEqual(
            req['close'],
            close)
        self.assertEqual(
            req['buy_price'],
            expected_buy_price)
        self.assertEqual(
            req['prev_shares'],
            expected_prev_shares)
        self.assertEqual(
            req['prev_balance'],
            use_balance)
        self.assertEqual(
            req['shares'],
            expected_num_shares)
        self.assertEqual(
            req['balance'],
            expected_balance)
        self.assertEqual(
            req['details'],
            details)
    # end of test_build_buy_order_not_enough_funds

    def test_build_sell_order(self):
        """test_build_sell_order"""
        use_key = 'test_build_sell_order'
        details = {
            'test': use_key
        }
        date = '2018-11-02'
        close = 280.00
        use_balance = self.balance
        commission = 11.5
        sell_num = 7  # (7 * 280) + 11.5 = 1971.5
        expected_sell_price = 1971.5
        expected_balance = use_balance + expected_sell_price
        expected_prev_shares = 13
        expected_num_shares = expected_prev_shares - sell_num
        req = build_sell_order.build_sell_order(
            ticker=self.ticker,
            close=close,
            balance=use_balance,
            commission=commission,
            details=details,
            date=date,
            num_owned=expected_prev_shares,
            shares=sell_num,
            use_key=use_key,
            reason='testing {}'.format(use_key))
        print(ae_consts.ppj(req))
        self.assertEqual(
            ae_consts.get_status(status=req['status']),
            'TRADE_FILLED')
        self.assertEqual(
            req['ticker'],
            self.ticker)
        self.assertEqual(
            req['close'],
            close)
        self.assertEqual(
            req['sell_price'],
            expected_sell_price)
        self.assertEqual(
            req['prev_shares'],
            expected_prev_shares)
        self.assertEqual(
            req['prev_balance'],
            use_balance)
        self.assertEqual(
            req['shares'],
            expected_num_shares)
        self.assertEqual(
            req['balance'],
            expected_balance)
        self.assertEqual(
            req['details'],
            details)
    # end of test_build_sell_order

    def test_build_sell_order_not_enough_funds(self):
        """test_build_sell_order_not_enough_funds"""
        use_key = 'test_build_sell_order_not_enough_funds'
        details = {
            'test': use_key
        }
        date = '2018-11-02'
        close = 280.00
        use_balance = 9.0  # if there's not enough to cover commissions
        commission = 11.5
        sell_num = 7  # (7 * 280) + 11.5 = 1971.5
        expected_sell_price = 0.0
        expected_balance = use_balance + expected_sell_price
        expected_prev_shares = 13
        expected_num_shares = expected_prev_shares - 0
        req = build_sell_order.build_sell_order(
            ticker=self.ticker,
            close=close,
            balance=use_balance,
            commission=commission,
            details=details,
            date=date,
            num_owned=expected_prev_shares,
            shares=sell_num,
            use_key=use_key,
            reason='testing {}'.format(use_key))
        print(ae_consts.ppj(req))
        self.assertEqual(
            ae_consts.get_status(status=req['status']),
            'TRADE_NOT_ENOUGH_FUNDS')
        self.assertEqual(
            req['ticker'],
            self.ticker)
        self.assertEqual(
            req['close'],
            close)
        self.assertEqual(
            req['sell_price'],
            expected_sell_price)
        self.assertEqual(
            req['prev_shares'],
            expected_prev_shares)
        self.assertEqual(
            req['prev_balance'],
            use_balance)
        self.assertEqual(
            req['shares'],
            expected_num_shares)
        self.assertEqual(
            req['balance'],
            expected_balance)
        self.assertEqual(
            req['details'],
            details)
    # end of test_build_sell_order_not_enough_funds

    def test_build_sell_order_not_owned_asset(self):
        """test_build_sell_order_not_owned_asset"""
        use_key = 'test_build_sell_order_not_owned_asset'
        details = {
            'test': use_key
        }
        date = '2018-11-02'
        close = 280.00
        use_balance = 42.0
        commission = 11.5
        sell_num = 7  # (7 * 280) + 11.5 = 1971.5
        expected_sell_price = 0.0
        expected_balance = use_balance + expected_sell_price
        expected_prev_shares = 0
        expected_num_shares = expected_prev_shares - 0
        req = build_sell_order.build_sell_order(
            ticker=self.ticker,
            close=close,
            balance=use_balance,
            commission=commission,
            details=details,
            date=date,
            num_owned=expected_prev_shares,
            shares=sell_num,
            use_key=use_key,
            reason='testing {}'.format(use_key))
        print(ae_consts.ppj(req))
        self.assertEqual(
            ae_consts.get_status(status=req['status']),
            'TRADE_NO_SHARES_TO_SELL')
        self.assertEqual(
            req['ticker'],
            self.ticker)
        self.assertEqual(
            req['close'],
            close)
        self.assertEqual(
            req['sell_price'],
            expected_sell_price)
        self.assertEqual(
            req['prev_shares'],
            expected_prev_shares)
        self.assertEqual(
            req['prev_balance'],
            use_balance)
        self.assertEqual(
            req['shares'],
            expected_num_shares)
        self.assertEqual(
            req['balance'],
            expected_balance)
        self.assertEqual(
            req['details'],
            details)
    # end of test_build_sell_order_not_owned_asset

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily(self):
        """test_run_daily"""
        test_name = 'test_run_daily'
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=self.balance,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        print(self.data)
        algo.handle_data(
            data=self.data)
    # end of test_run_daily

    @mock.patch(
        ('analysis_engine.ae_talib.WILLR'),
        new=mock_talib.MockWILLRBuy)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_daily_with_config(self):
        """test_run_daily_with_config"""
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=self.balance,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            config_dict=self.algo_config_dict)
        self.assertEqual(
            algo.name,
            self.algo_config_dict['name'])
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        print(self.data)
        algo.handle_data(
            data=self.data)
    # end of test_run_daily_with_config

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_algo_daily(self):
        """test_run_algo_daily"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        rec = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        print(rec)
    # end of test_run_algo_daily

    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_algo_config_dict_assignments(self):
        """test_algo_config_dict_assignments"""
        ticker = 'SPY'
        config_dict = {
            'latest_high': 800.0,
            'latest_low': 100.0,
            'latest_open': 300.0,
            'latest_close': 400.0,
            'latest_volume': 500,
            'num_owned': 7,
            'balance': 2000.0
        }
        demo_algo = base_algo.BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
            config_dict=config_dict,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name='test-{}'.format(ticker))
        self.assertEqual(
            demo_algo.latest_high,
            config_dict['latest_high'])
        self.assertEqual(
            demo_algo.latest_low,
            config_dict['latest_low'])
        self.assertEqual(
            demo_algo.latest_open,
            config_dict['latest_open'])
        self.assertEqual(
            demo_algo.latest_close,
            config_dict['latest_close'])
        self.assertEqual(
            demo_algo.latest_volume,
            config_dict['latest_volume'])
        self.assertEqual(
            demo_algo.num_owned,
            config_dict['num_owned'])
        self.assertEqual(
            demo_algo.balance,
            config_dict['balance'])
    # end of test_algo_config_dict_assignments

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_sample_algo_code_in_docstring(self):
        """test_sample_algo_code_in_docstring"""
        ticker = 'SPY'
        demo_algo = base_algo.BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name='test-{}'.format(ticker))
        date = '2018-11-05'
        dataset_id = '{}_{}'.format(
            ticker,
            date)

        # mock the data pipeline in redis:
        data = {
            ticker: [
                {
                    'id': dataset_id,
                    'date': date,
                    'data': {
                        'daily': pd.DataFrame([
                            {
                                'high': 280.01,
                                'low': 270.01,
                                'open': 275.01,
                                'close': 272.02,
                                'volume': 123,
                                'date': '2018-11-01 15:59:59'
                            },
                            {
                                'high': 281.01,
                                'low': 271.01,
                                'open': 276.01,
                                'close': 273.02,
                                'volume': 124,
                                'date': '2018-11-02 15:59:59'
                            },
                            {
                                'high': 282.01,
                                'low': 272.01,
                                'open': 277.01,
                                'close': 274.02,
                                'volume': 121,
                                'date': '2018-11-05 15:59:59'
                            }
                        ]),
                        'calls': pd.DataFrame([]),
                        'puts': pd.DataFrame([]),
                        'minute': pd.DataFrame([]),
                        'pricing': pd.DataFrame([]),
                        'quote': pd.DataFrame([]),
                        'news': pd.DataFrame([]),
                        'news1': pd.DataFrame([]),
                        'dividends': pd.DataFrame([]),
                        'earnings': pd.DataFrame([]),
                        'financials': pd.DataFrame([]),
                        'stats': pd.DataFrame([]),
                        'peers': pd.DataFrame([]),
                        'tdcalls': pd.DataFrame([]),
                        'tdputs': pd.DataFrame([]),
                        'company': pd.DataFrame([])
                        # DEFAULT_SERIALIZED_DATASETS
                    }
                }
            ]
        }

        # run the algorithm
        demo_algo.handle_data(data=data)

        # get the algorithm results
        results = demo_algo.get_result()

        print(ae_consts.ppj(results))
        print(results['history'][0].get('err', 'no error'))
        self.assertEqual(
            results['balance'],
            1000.0)
        self.assertEqual(
            len(results['history']),
            1)
        self.assertEqual(
            ae_consts.get_status(results['history'][0]['status']),
            'TRADE_NOT_PROFITABLE')
        self.assertEqual(
            ae_consts.get_status(results['history'][0]['algo_status']),
            'ALGO_NOT_PROFITABLE')
        demo_algo.loaded_dataset = demo_algo.last_handle_data
        self.validate_dataset_structure(cur_algo=demo_algo)
    # end of test_sample_algo_code_in_docstring

    def test_trade_history_algo_not_trade_profitable(self):
        history = build_trade_history_entry.build_trade_history_entry(
            ticker='notreal',
            original_balance=1000.00,
            num_owned=20,
            algo_start_price=270.01,
            close=280.41,
            balance=123,
            commission=6,
            ds_id='SPY_2018-11-02',
            date='today',
            trade_type=ae_consts.TRADE_SHARES)
        print(history.get('err', 'no error'))
        self.assertEqual(
            ae_consts.get_status(status=history['status']),
            'TRADE_PROFITABLE')
        self.assertEqual(
            ae_consts.get_status(status=history['algo_status']),
            'ALGO_NOT_PROFITABLE')
        self.assertEqual(
            history['balance'],
            123)
        self.assertEqual(
            history['commission'],
            6)
        self.assertEqual(
            history['close'],
            280.41)
        self.assertEqual(
            history['net_gain'],
            None)
    # end of test_trade_history_algo_not_trade_profitable

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_run_derived_algo_daily(self):
        """test_run_derived_algo_daily"""
        test_name = 'test_run_derived_algo_daily'
        balance = self.balance
        commission = 13.5

        class DerivedAlgoTest(base_algo.BaseAlgo):
            """
            # alternative inheritance - python 2
            def __init__(
                    self,
                    ticker,
                    balance,
                    commission=6.0,
                    tickers=None,
                    name=None,
                    auto_fill=True,
                    timeseries=None,
                    trade_strategy=None,
                    config_dict=None):
                BaseAlgo.__init__(
                    self,
                    ticker=ticker,
                    balance=balance,
                    commission=commission,
                    tickers=tickers,
                    name=name,
                    auto_fill=auto_fill,
                    timeseries=None,
                    trade_strategy=None,
                    config_dict=config_dict)
            """

            def __init__(
                    self,
                    ticker,
                    balance,
                    commission=6.0,
                    tickers=None,
                    name=None,
                    auto_fill=True,
                    timeseries=None,
                    trade_strategy=None,
                    config_dict=None):
                """__init__

                :param ticker: test ticker
                :param balance: test balance
                :param commission: test commission
                :param tickers: test tickers
                :param name: name of algo
                :param auto_fill: auto fill trade for backtesting
                :param config_dict: config_dict
                """
                if config_dict:
                    config_dict['verbose'] = True
                super(DerivedAlgoTest, self).__init__(
                    ticker=ticker,
                    balance=balance,
                    commission=commission,
                    tickers=tickers,
                    name=name,
                    auto_fill=auto_fill,
                    timeseries=timeseries,
                    trade_strategy=trade_strategy,
                    config_dict=config_dict,
                    verbose=True)

                self.daily_results = []
                self.num_daily_found = 0
            # end of __init__

            def process(
                    self,
                    algo_id,
                    ticker,
                    dataset):
                """process

                derived process method

                :param algo_id: algorithm id
                :param ticker: ticker
                :param dataset: datasets for this date
                """
                self.daily_results.append(dataset)

                assert(hasattr(self.df_daily, 'index'))
                assert(hasattr(self.df_minute, 'index'))
                assert(hasattr(self.df_puts, 'index'))
                assert(hasattr(self.df_calls, 'index'))
                assert(hasattr(self.df_pricing, 'index'))
                assert(hasattr(self.df_quote, 'index'))
                assert(hasattr(self.df_stats, 'index'))
                assert(hasattr(self.df_peers, 'index'))
                assert(hasattr(self.df_iex_news, 'index'))
                assert(hasattr(self.df_financials, 'index'))
                assert(hasattr(self.df_earnings, 'index'))
                assert(hasattr(self.df_dividends, 'index'))
                assert(hasattr(self.df_company, 'index'))
                assert(hasattr(self.df_yahoo_news, 'index'))

                self.num_daily_found += len(self.df_daily.index)
            # end of process

            def get_test_values(
                    self):
                """get_test_values"""
                return self.daily_results
            # end of get_test_values

            def get_num_daily_found(
                    self):
                """get_test_values"""
                return self.num_daily_found
            # end of get_num_daily_found

        # end of DerivedAlgoTest

        algo = DerivedAlgoTest(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        print(f'starting algo {datetime.datetime.now()}')
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True,
            verbose=True)
        print(ae_consts.ppj(algo_res))
        print(f'done algo {datetime.datetime.now()}')
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        self.assertTrue(
            len(algo.get_test_values()) >= 1)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            ae_consts.get_status(status=algo_res['status']),
            'SUCCESS')
        self.assertEqual(
            len(algo_res['rec']['history']),
            len(algo.get_test_values()))
        print(
            f'dates: {self.use_start_date_str} to {self.use_end_date_str}')
    # end of test_run_derived_algo_daily

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=mock_s3.build_boto3_resource)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_algo_can_save_all_input_datasets_publish_disabled(self):
        """test_algo_can_save_all_input_datasets_publish_disabled"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            publish_history=False,
            publish_report=False,
            publish_input=False,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        output_file = '/opt/ae/tests/datasets/algo/{}.json'.format(
            test_name)
        redis_enabled = False
        redis_key = '{}'.format(
            test_name)
        s3_enabled = False
        s3_key = '{}.json'.format(
            test_name)
        compress = False
        slack_enabled = False
        slack_code_block = True
        slack_full_width = False
        verbose = True
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=output_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'NOT_RUN')
    # end of test_algo_can_save_all_input_datasets_publish_disabled

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=mock_s3.build_boto3_resource)
    @mock.patch(
        ('requests.post'),
        new=mock_request_success_result)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file)
    def test_algo_can_save_all_input_datasets_to_file(self):
        """test_algo_can_save_all_input_datasets_to_file"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        output_file = '/opt/ae/tests/datasets/algo/{}.json'.format(
            test_name)
        redis_enabled = True
        redis_key = '{}'.format(
            test_name)
        s3_enabled = True
        s3_key = '{}.json'.format(
            test_name)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=output_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
    # end of test_algo_can_save_all_input_datasets_to_file

    @mock.patch(
        ('redis.Redis'),
        new=mock_redis.MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=mock_s3.build_boto3_resource)
    @mock.patch(
        ('requests.post'),
        new=mock_request_success_result)
    @mock.patch(
        ('analysis_engine.write_to_file.write_to_file'),
        new=mock_write_to_file_failed)
    def test_algo_can_save_all_input_datasets_to_file_failed(self):
        """test_algo_can_save_all_input_datasets_to_file_failed"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        output_file = '/opt/ae/tests/datasets/algo/{}.json'.format(
            test_name)
        redis_enabled = True
        redis_key = '{}'.format(
            test_name)
        s3_enabled = True
        s3_key = '{}.json'.format(
            test_name)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=output_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'FILE_FAILED')
    # end of test_algo_can_save_all_input_datasets_to_file_failed

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

    def test_integration_algo_publish_input_dataset_to_redis(self):
        """test_integration_algo_publish_input_dataset_to_redis"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_publish_input_dataset_to_redis')
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        output_file = '/opt/ae/tests/datasets/algo/{}.json'.format(
            test_name)
        redis_enabled = True
        redis_key = '{}'.format(
            test_name)
        s3_enabled = True
        s3_key = '{}.json'.format(
            test_name)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=output_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
        redis_res = redis_get.get_data_from_redis_key(
            host=publish_input_req['redis_address'].split(':')[0],
            port=publish_input_req['redis_address'].split(':')[1],
            password=publish_input_req['redis_password'],
            db=publish_input_req['redis_db'],
            key=publish_input_req['redis_key'],
            serializer=publish_input_req['redis_serializer'],
            encoding=publish_input_req['redis_encoding'])
        self.assertEqual(
            ae_consts.get_status(status=redis_res['status']),
            'SUCCESS')
        print('found data size={} in redis_key={}'.format(
            len(redis_res['rec']['data']),
            publish_input_req['redis_key']))
        self.assertTrue(
            len(redis_res['rec']['data']) > 10)
    # end of test_integration_algo_publish_input_dataset_to_redis

    def test_integration_algo_publish_input_dataset_to_file(self):
        """test_integration_algo_publish_input_dataset_to_file"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_publish_input_dataset_to_file')
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        test_should_create_this_file = (
            '/opt/ae/tests/datasets/algo/{}-{}.json'.format(
                test_name,
                str(uuid.uuid4())))
        redis_enabled = True
        redis_key = '{}'.format(
            test_name)
        s3_enabled = True
        s3_key = '{}.json'.format(
            test_name)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
        self.assertTrue(os.path.exists(test_should_create_this_file))
        # now load it into an algo
    # end of test_integration_algo_publish_input_dataset_to_file

    def test_integration_algo_load_from_file(self):
        """test_integration_algo_load_from_file"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_load_from_file')
        test_file_regex = (
            '{}/test_integration_algo_load_from_file'
            '*.json'.format(
                self.output_dir))
        files = sorted(
            glob.iglob(test_file_regex),
            key=os.path.getctime,
            reverse=True)

        load_config_req = None
        latest_file = (
            '/opt/ae/tests/datasets/algo/{}-{}.json'.format(
                test_name,
                str(uuid.uuid4())))
        if len(files) == 0:
            algo = base_algo.BaseAlgo(
                ticker=self.ticker,
                balance=self.balance,
                commission=6.0,
                timeseries=self.timeseries,
                trade_strategy=self.trade_strategy,
                name=test_name)
            run_algo.run_algo(
                ticker=self.ticker,
                algo=algo,
                start_date=self.use_start_date_str,
                end_date=self.use_end_date_str,
                label=test_name,
                raise_on_err=True)
            publish_input_req = build_publish_request.build_publish_request(
                label=test_name,
                output_file=latest_file,
                convert_to_json=True,
                compress=False,
                redis_enabled=False,
                s3_enabled=False,
                slack_enabled=False,
                verbose=True)
            publish_input_status = \
                algo.publish_input_dataset(
                    **publish_input_req)
            self.assertEqual(
                ae_consts.get_status(status=publish_input_status),
                'SUCCESS')
        else:
            latest_file = files[0]
        # end of create a file

        self.assertTrue(os.path.exists(latest_file))

        load_config_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=latest_file,
            compress=False,
            redis_enabled=False,
            s3_enabled=False)
        file_algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=self.balance,
            commission=6.0,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name='load-from-file_{}'.format(
                test_name),
            load_config=load_config_req)

        print(file_algo.loaded_dataset)
        self.validate_dataset_structure(cur_algo=file_algo)
    # end of test_integration_algo_load_from_file

    def test_integration_algo_publish_input_s3_and_load(self):
        """test_integration_algo_publish_input_s3_and_load"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_publish_input_s3_and_load')
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        unique_id = str(uuid.uuid4())
        test_should_create_this_file = (
            '/opt/ae/tests/datasets/algo/{}-{}.json'.format(
                test_name,
                unique_id))
        redis_enabled = True
        redis_key = '{}:{}'.format(
            test_name,
            unique_id)
        s3_enabled = True
        s3_key = '{}-{}.json'.format(
            test_name,
            unique_id)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        redis_db = 1
        unittest_bucket = 'unittest-algo'
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=redis_db,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        load_config_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=redis_db,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
        self.assertTrue(os.path.exists(test_should_create_this_file))
        # now load it into an algo

        print('')
        print('---------------')
        print('starting s3 load integration test')

        load_config_req['s3_key'] = s3_key
        s3_algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            name=test_name,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            load_config=load_config_req)

        self.validate_dataset_structure(cur_algo=s3_algo)
    # end of test_integration_algo_publish_input_s3_and_load

    def test_integration_algo_publish_input_redis_and_load(self):
        """test_integration_algo_publish_input_redis_and_load"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_publish_input_redis_and_load')
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        unique_id = str(uuid.uuid4())
        test_should_create_this_file = (
            '/opt/ae/tests/datasets/algo/{}-{}.json'.format(
                test_name,
                unique_id))
        redis_enabled = True
        redis_key = '{}:{}'.format(
            test_name,
            unique_id)
        s3_enabled = True
        s3_key = '{}-{}.json'.format(
            test_name,
            unique_id)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        redis_db = 1
        unittest_bucket = 'unittest-algo'
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=redis_db,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        load_config_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=redis_db,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
        self.assertTrue(os.path.exists(test_should_create_this_file))
        # now load it into an algo

        print('')
        print('---------------')
        print('starting redis publish integration test')

        load_config_req['redis_key'] = s3_key
        redis_algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            name=test_name,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            load_config=load_config_req)

        self.validate_dataset_structure(cur_algo=redis_algo)
    # end of test_integration_algo_publish_input_redis_and_load

    def test_integration_algo_restore_ready_back_to_redis(self):
        """test_integration_algo_restore_ready_back_to_redis"""
        if ae_consts.ev('INT_TESTS', '0') == '0':
            return

        test_name = (
            'test_integration_algo_restore_ready_back_to_redis')
        balance = self.balance
        commission = 13.5
        algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            name=test_name)
        algo_res = run_algo.run_algo(
            ticker=self.ticker,
            algo=algo,
            start_date=self.use_start_date_str,
            end_date=self.use_end_date_str,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) >= 1)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        unique_id = str(uuid.uuid4())
        test_should_create_this_file = (
            '/opt/ae/tests/datasets/algo/{}-{}.json'.format(
                test_name,
                unique_id))
        redis_enabled = True
        redis_key = '{}:{}'.format(
            test_name,
            unique_id)
        s3_enabled = True
        s3_key = '{}-{}.json'.format(
            test_name,
            unique_id)
        compress = False
        slack_enabled = True
        slack_code_block = True
        slack_full_width = False
        verbose = True
        unittest_bucket = 'unittest-algo'
        publish_input_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=1,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        load_config_req = build_publish_request.build_publish_request(
            label=test_name,
            convert_to_json=True,
            output_file=test_should_create_this_file,
            compress=compress,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_db=1,  # publish to the redis database 1
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_bucket=unittest_bucket,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose)
        publish_input_status = algo.publish_input_dataset(
            **publish_input_req)
        self.assertEqual(
            ae_consts.get_status(status=publish_input_status),
            'SUCCESS')
        self.assertTrue(os.path.exists(test_should_create_this_file))
        # now load it into an algo

        print('')
        print('---------------')
        print('starting redis publish integration test')

        load_config_req['redis_key'] = s3_key
        redis_algo = base_algo.BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            name=test_name,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            load_config=load_config_req)

        self.validate_dataset_structure(cur_algo=redis_algo)
    # end of test_integration_algo_restore_ready_back_to_redis

# end of TestBaseAlgo
