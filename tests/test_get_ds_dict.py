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
        base_key = '{}_{}'.format(
            self.ticker,
            self.last_close_str)
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
            '{}_daily'.format(
                base_key))
        self.assertEqual(
            cache_dict['minute'],
            '{}_minute'.format(
                base_key))
        self.assertEqual(
            cache_dict['quote'],
            '{}_quote'.format(
                base_key))
        self.assertEqual(
            cache_dict['stats'],
            '{}_stats'.format(
                base_key))
        self.assertEqual(
            cache_dict['peers'],
            '{}_peers'.format(
                base_key))
        self.assertEqual(
            cache_dict['news1'],
            '{}_news1'.format(
                base_key))
        self.assertEqual(
            cache_dict['financials'],
            '{}_financials'.format(
                base_key))
        self.assertEqual(
            cache_dict['earnings'],
            '{}_earnings'.format(
                base_key))
        self.assertEqual(
            cache_dict['dividends'],
            '{}_dividends'.format(
                base_key))
        self.assertEqual(
            cache_dict['company'],
            '{}_company'.format(
                base_key))
        self.assertEqual(
            cache_dict['options'],
            '{}_options'.format(
                base_key))
        self.assertEqual(
            cache_dict['pricing'],
            '{}_pricing'.format(
                base_key))
        self.assertEqual(
            cache_dict['news'],
            '{}_news'.format(
                base_key))
        self.assertEqual(
            cache_dict['version'],
            CACHE_DICT_VERSION)
    # end of test_get_ds_dict

# end of TestBuildDatasetCacheDict
