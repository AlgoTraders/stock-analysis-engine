"""
Test file for classes and functions:

- analysis_engine.indicators.load_indicator_from_module
- analysis_engine.indicators.indicator_processor

"""

import analysis_engine.consts as ae_consts
import analysis_engine.indicators.load_indicator_from_module as load_ind
from analysis_engine.mocks.base_test import BaseTestCase


class TestLoadIndicatorFromFile(BaseTestCase):
    """TestLoadIndicatorFromFile"""

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
                    "name": "willr",
                    "module_path": self.example_module_path,
                    "category": "technical",
                    "type": "momentum",
                    "dataset_df": "daily",
                    "num_points": 19,
                    "buy_above": 80,
                    "sell_below": 10
                },
                {
                    "name": "willr",
                    "module_path": self.example_module_path,
                    "category": "technical",
                    "type": "momentum",
                    "dataset_df": "daily",
                    "num_points": 15,
                    "buy_above": 60,
                    "sell_below": 20
                },
                {
                    "name": "baseindicator",
                    "category": "fundamental",
                    "type": "balance_sheet",
                    "dataset_df": "daily"
                }
            ],
            "slack": {
                "webhook": None
            }
        }
    # end of setUp

    def test_load_indicator_from_example_indicator_file(self):
        """test_load_indicator_from_example_indicator_file"""
        log_label = 'my_ind_1'
        ind_1 = load_ind.load_indicator_from_module(
            module_name='ExampleIndicatorWilliamsR',
            log_label=log_label,
            path_to_module=self.example_module_path,
            ind_dict=self.test_data['indicators'][0])
        self.assertTrue(
            ind_1 is not None)
        self.assertEqual(
            ind_1.get_name(),
            log_label)
    # end of test_load_indicator_from_example_indicator_file

    def test_load_multiple_indicator_from_same_example_indicator_file(self):
        """test_load_multiple_indicator_from_same_example_indicator_file"""
        log_label_1 = 'my_ind_1'
        log_label_2 = 'my_ind_2'
        log_label_3 = 'base_ind_1'
        ind_1 = load_ind.load_indicator_from_module(
            module_name='ExampleIndicatorWilliamsR',
            log_label=log_label_1,
            path_to_module=self.example_module_path,
            ind_dict=self.test_data['indicators'][0])
        self.assertTrue(
            ind_1 is not None)
        self.assertEqual(
            ind_1.get_name(),
            log_label_1)
        ind_2 = load_ind.load_indicator_from_module(
            module_name='ExampleIndicatorWilliamsR',
            log_label=log_label_2,
            path_to_module=self.example_module_path,
            ind_dict=self.test_data['indicators'][1])
        self.assertTrue(
            ind_2 is not None)
        self.assertEqual(
            ind_2.get_name(),
            log_label_2)
        self.assertEqual(
            ind_1.get_path_to_module(),
            ind_2.get_path_to_module())
        ind_3 = load_ind.load_indicator_from_module(
            module_name='BaseIndicator',
            log_label=log_label_3,
            ind_dict=self.test_data['indicators'][2])
        self.assertEqual(
            ind_3.get_path_to_module(),
            ae_consts.INDICATOR_BASE_MODULE_PATH)
        self.assertEqual(
            ind_3.get_name(),
            log_label_3)
    # end of test_load_indicator_from_example_indicator_file

# end of TestLoadIndicatorFromFile
