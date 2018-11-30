"""
Test file for classes and functions:

- analysis_engine.indicators.base_indicator
- analysis_engine.indicators.indicator_processor

"""

import analysis_engine.consts as ae_consts
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
        self.example_module_path = (
            'analysis_engine/mocks/example_indicator_williamsr.py')
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
                    "name": "willr_1",
                    "module_path": self.example_module_path,
                    "category": "technical",
                    "type": "momentum",
                    "uses_data": "daily",
                    "num_points": 19,
                    "buy_above": 80,
                    "sell_below": 10
                },
                {
                    "name": "willr_2",
                    "module_path": self.example_module_path,
                    "category": "technical",
                    "type": "momentum",
                    "uses_data": "daily",
                    "num_points": 15,
                    "buy_above": 60,
                    "sell_below": 20
                },
                {
                    "name": "baseindicator",
                    "category": "fundamental",
                    "type": "balance_sheet",
                    "uses_data": "daily"
                }
            ],
            "slack": {
                "webhook": None
            }
        }
    # end of setUp

    def test_build_indicator_processor(self):
        """test_build_algo_request_daily"""
        print(self.test_data)
        proc = IndicatorProcessor(
            config_dict=self.test_data)
        self.assertTrue(
            len(proc.get_indicators()) == 3)
        indicators = proc.get_indicators()
        for idx, ind_id in enumerate(indicators):
            ind_node = indicators[ind_id]
            print(ind_node)
            self.assertTrue(
                ind_node['obj'] is not None)
            if idx == 2:
                self.assertEqual(
                    ind_node['report']['path_to_module'],
                    ae_consts.INDICATOR_BASE_MODULE_PATH)
            else:
                self.assertEqual(
                    ind_node['report']['path_to_module'],
                    self.example_module_path)
    # end of test_build_indicator_processor

# end of TestIndicatorProcessor
