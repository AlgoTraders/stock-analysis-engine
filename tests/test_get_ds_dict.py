"""
Test file for:
Build Dataset Cache Dict
"""

from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import CACHE_DICT_VERSION
from analysis_engine.consts import COMMON_DATE_FORMAT
from analysis_engine.utils import get_last_close_str
from analysis_engine.api_requests import get_ds_dict


class TestBuildDatasetCacheDict(BaseTestCase):
    """TestBuildDatasetCacheDict"""

    ticker = None
    last_close_str = None

    def setUp(
            self):
        """setUp"""
        self.ticker = 'AAPL'
        self.last_close_str = get_last_close_str(fmt=COMMON_DATE_FORMAT)
    # end of setUp

    def test_get_ds_dict(self):
        """test_get_ds_dict"""
        test_name = 'test_build_dataset_cache_dict'
        base_key = f'{self.ticker}_{self.last_close_str}'
        cache_dict = get_ds_dict(
            ticker=self.ticker,
            label=test_name)

        self.assertIsNotNone(
            cache_dict)
        self.assertEqual(
            cache_dict['ticker'],
            self.ticker)
        self.assertEqual(
            cache_dict['daily'],
            f'{base_key}_daily')
        self.assertEqual(
            cache_dict['minute'],
            f'{base_key}_minute')
        self.assertEqual(
            cache_dict['quote'],
            f'{base_key}_quote')
        self.assertEqual(
            cache_dict['stats'],
            f'{base_key}_stats')
        self.assertEqual(
            cache_dict['peers'],
            f'{base_key}_peers')
        self.assertEqual(
            cache_dict['news1'],
            f'{base_key}_news1')
        self.assertEqual(
            cache_dict['financials'],
            f'{base_key}_financials')
        self.assertEqual(
            cache_dict['earnings'],
            f'{base_key}_earnings')
        self.assertEqual(
            cache_dict['dividends'],
            f'{base_key}_dividends')
        self.assertEqual(
            cache_dict['company'],
            f'{base_key}_company')
        self.assertEqual(
            cache_dict['options'],
            f'{base_key}_options')
        self.assertEqual(
            cache_dict['pricing'],
            f'{base_key}_pricing')
        self.assertEqual(
            cache_dict['news'],
            f'{base_key}_news')
        self.assertEqual(
            cache_dict['version'],
            CACHE_DICT_VERSION)
    # end of test_get_ds_dict

# end of TestBuildDatasetCacheDict
