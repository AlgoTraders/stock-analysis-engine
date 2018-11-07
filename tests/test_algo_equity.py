"""
Test file for:
Build Dataset Cache Dict
"""

import pandas as pd
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import COMMON_DATE_FORMAT
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
        details = {
            'test': use_key
        }
        req = build_buy_order(
            ticker=self.ticker,
            close=280.00,
            balance=self.balance,
            commission=12.0,
            details=details,
            date='2018-11-02',
            num_owned=10,
            shares=5,
            use_key=use_key,
            reason='testing {}'.format(use_key))
        self.assertEqual(
            req['ticker'],
            self.ticker)
        print(req)
    # end of test_build_buy_order

    def test_build_sell_order(self):
        """test_build_sell_order"""
        use_key = 'test_build_sell_order'
        details = {
            'test': use_key
        }
        req = build_sell_order(
            ticker=self.ticker,
            close=280.00,
            balance=self.balance,
            commission=12.0,
            details=details,
            date='2018-11-02',
            num_owned=13,
            shares=5,
            use_key=use_key,
            reason='testing {}'.format(use_key))
        self.assertEqual(
            req['ticker'],
            self.ticker)
        print(req)
    # end of test_build_sell_order

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
