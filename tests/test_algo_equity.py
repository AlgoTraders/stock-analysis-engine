"""
Test file for:
Build Dataset Cache Dict
"""

import pandas as pd
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import COMMON_DATE_FORMAT
from analysis_engine.consts import ppj
from analysis_engine.consts import get_status
from analysis_engine.utils import get_last_close_str
from analysis_engine.api_requests import build_algo_request
from analysis_engine.api_requests import build_buy_order
from analysis_engine.api_requests import build_sell_order
from analysis_engine.algo import EquityAlgo


class TestAlgoEquity(BaseTestCase):
    """TestAlgoEquity"""

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
        self.daily_df_name = '{}_2018-11-05_daily'.format(
            self.ticker)
        self.minute_df_name = '{}_2018-11-05_minute'.format(
            self.ticker)
        self.options_df_name = '{}_2018-11-05_options'.format(
            self.ticker)
        self.datasets = [
            'daily'
        ]
        self.data = {}
        self.data[self.ticker] = [
            {
                'name': self.daily_df_name,
                'valid': True,
                'df': self.daily_df
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
        algo = EquityAlgo(
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

# end of TestAlgoEquity
