"""
Test file for classes and functions:

- analysis_engine.indicators.indicator_processor

"""

from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.indicators.indicator_processor import IndicatorProcessor


class TestIndicatorProcessor(BaseTestCase):
    """TestIndicatorProcessor"""

    ticker = None
    last_close_str = None

    def setUp(
            self):
        """setUp"""
        self.ticker = 'SPY'
        self.test_data = {
            "name": "test_5_days_ahead",
            "algo_module_path": None,
            "algo_version": 1,
            "trade_horizon_units": "day",
            "trade_horizon": 5,
            "buy_rules": {
                "confidence": 75,
                "min_indicators": 1
            },
            "sell_rules": {
                "confidence": 75,
                "min_indicators": 1
            },
            "indicators": [
                {
                    "name": "bollingerbands",
                    "category": "technical",
                    "type": "momentum",
                    "uses_data": "daily",
                    "num_points": 12,
                    "buy_above": 60,
                    "sell_below": 20
                },
                {
                    "name": "willr",
                    "category": "technical",
                    "type": "momentum",
                    "uses_data": "daily",
                    "num_points": 15,
                    "buy_above": 60,
                    "sell_below": 20
                }
            ],
            "slack": {
                "webhook": None
            }
        }
    # end of setUp

    def test_build_indicator_processor(self):
        """test_build_algo_request_daily"""
        ind = IndicatorProcessor(
            config_dict=self.test_data)
        self.assertTrue(
            len(ind.ind_dict) == 2)
    # end of test_build_indicator_processor

# end of TestIndicatorProcessor
