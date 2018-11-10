"""
Test file for classes and functions:

- analysis_engine.algo.BaseAlgo
- analysis_engine.run_algo.run_algo
- analysis_engine.build_algo_request
- analysis_engine.build_buy_order
- analysis_engine.build_sell_order
- analysis_engine.build_trade_history_entry

"""

import pandas as pd
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import COMMON_DATE_FORMAT
from analysis_engine.consts import TRADE_SHARES
from analysis_engine.consts import ppj
from analysis_engine.consts import get_status
from analysis_engine.utils import get_last_close_str
from analysis_engine.build_algo_request import build_algo_request
from analysis_engine.build_buy_order import build_buy_order
from analysis_engine.build_sell_order import build_sell_order
from analysis_engine.build_trade_history_entry import build_trade_history_entry
from analysis_engine.algo import BaseAlgo
from analysis_engine.run_algo import run_algo


class TestBaseAlgo(BaseTestCase):
    """TestBaseAlgo"""

    ticker = None
    last_close_str = None

    def setUp(
            self):
        """setUp"""
        self.ticker = 'SPY'
        self.start_date_str = (
            '2018-11-01 15:59:59'  # Thursday
        )
        self.end_date_str = (
            '2018-11-05 15:59:59'  # Monday
        )
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
        self.last_close_str = get_last_close_str(fmt=COMMON_DATE_FORMAT)
    # end of setUp

    def test_build_algo_request_daily(self):
        """test_build_algo_request_daily"""
        use_key = 'test_build_algo_request_daily'
        req = build_algo_request(
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
        req = build_buy_order(
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
        print(ppj(req))
        self.assertEqual(
            get_status(status=req['status']),
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
        req = build_buy_order(
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
        print(ppj(req))
        self.assertEqual(
            get_status(status=req['status']),
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
        req = build_sell_order(
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
        print(ppj(req))
        self.assertEqual(
            get_status(status=req['status']),
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
        req = build_sell_order(
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
        print(ppj(req))
        self.assertEqual(
            get_status(status=req['status']),
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
        req = build_sell_order(
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
        print(ppj(req))
        self.assertEqual(
            get_status(status=req['status']),
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

    def test_run_daily(self):
        """test_run_daily"""
        test_name = 'test_run_daily'
        algo = BaseAlgo(
            ticker=self.ticker,
            balance=self.balance,
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

    def test_run_algo_daily(self):
        """test_run_algo_daily"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            name=test_name)
        rec = run_algo(
            ticker=self.ticker,
            algo=algo,
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
        demo_algo = BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
            config_dict=config_dict,
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

    def test_sample_algo_code_in_docstring(self):
        """test_sample_algo_code_in_docstring"""
        ticker = 'SPY'
        demo_algo = BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
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
                        'minute': pd.DataFrame([]),
                        'news': pd.DataFrame([]),
                        'options': pd.DataFrame([])
                        # etc
                    }
                }
            ]
        }

        # run the algorithm
        demo_algo.handle_data(data=data)

        # get the algorithm results
        results = demo_algo.get_result()

        print(ppj(results))
        print(results['history'][0].get('err', 'no error'))
        self.assertEqual(
            results['balance'],
            1000.0)
        self.assertEqual(
            len(results['history']),
            1)
        self.assertEqual(
            get_status(results['history'][0]['status']),
            'TRADE_NOT_PROFITABLE')
        self.assertEqual(
            get_status(results['history'][0]['algo_status']),
            'ALGO_NOT_PROFITABLE')
    # end of test_sample_algo_code_in_docstring

    def test_trade_history_algo_not_trade_profitable(self):
        history = build_trade_history_entry(
            ticker='notreal',
            original_balance=1000.00,
            num_owned=20,
            algo_start_price=270.01,
            close=280.41,
            balance=123,
            commission=6,
            ds_id='SPY_2018-11-02',
            date='today',
            trade_type=TRADE_SHARES)
        print(history.get('err', 'no error'))
        self.assertEqual(
            get_status(status=history['status']),
            'TRADE_PROFITABLE')
        self.assertEqual(
            get_status(status=history['algo_status']),
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
            0.0)
    # end of test_trade_history_algo_not_trade_profitable

    def test_run_derived_algo_daily(self):
        """test_run_derived_algo_daily"""
        test_name = 'test_run_derived_algo_daily'
        balance = self.balance
        commission = 13.5

        class DerivedAlgoTest(BaseAlgo):
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
                    config_dict=None):
                BaseAlgo.__init__(
                    self,
                    ticker=ticker,
                    balance=balance,
                    commission=commission,
                    tickers=tickers,
                    name=name,
                    auto_fill=auto_fill,
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
                super().__init__(
                    ticker=ticker,
                    balance=balance,
                    commission=commission,
                    tickers=tickers,
                    name=name,
                    auto_fill=auto_fill,
                    config_dict=config_dict)

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
                assert(hasattr(self.df_daily, 'index'))
                assert(hasattr(self.df_minute, 'index'))
                assert(hasattr(self.df_quote, 'index'))
                assert(hasattr(self.df_stats, 'index'))
                assert(hasattr(self.df_peers, 'index'))
                assert(hasattr(self.df_iex_news, 'index'))
                assert(hasattr(self.df_financials, 'index'))
                assert(hasattr(self.df_earnings, 'index'))
                assert(hasattr(self.df_dividends, 'index'))
                assert(hasattr(self.df_company, 'index'))
                assert(hasattr(self.df_yahoo_news, 'index'))
                assert(hasattr(self.df_options, 'index'))
                assert(hasattr(self.df_pricing, 'index'))

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
            name=test_name)
        algo_res = run_algo(
            ticker=self.ticker,
            algo=algo,
            label=test_name,
            raise_on_err=True)
        print(ppj(algo_res))
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        self.assertTrue(
            len(algo.get_test_values()) > 30)
        self.assertTrue(
            len(algo_res['rec']['history']) > 30)
        self.assertEqual(
            get_status(status=algo_res['status']),
            'SUCCESS')
        self.assertEqual(
            len(algo_res['rec']['history']),
            len(algo.get_test_values()))
    # end of test_run_derived_algo_daily

    def test_algo_can_save_all_input_datasets_to_file(self):
        """test_algo_can_save_all_input_datasets_to_file"""
        test_name = 'test_run_algo_daily'
        balance = self.balance
        commission = 13.5
        algo = BaseAlgo(
            ticker=self.ticker,
            balance=balance,
            commission=commission,
            name=test_name)
        algo_res = run_algo(
            ticker=self.ticker,
            algo=algo,
            label=test_name,
            raise_on_err=True)
        self.assertTrue(
            len(algo_res['rec']['history']) > 30)
        self.assertEqual(
            algo.name,
            test_name)
        self.assertEqual(
            algo.tickers,
            [self.ticker])
        print(algo_res)
    # end of test_algo_can_save_all_input_datasets_to_file

# end of TestBaseAlgo
