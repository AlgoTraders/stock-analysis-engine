"""
Test file for:
update prices
"""

import mock
import tests.mock_pinance
from tests.base_test import BaseTestCase
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ERR
from analysis_engine.work_tasks.get_new_pricing_data \
    import run_get_new_pricing_data
from analysis_engine.api_requests \
    import build_get_new_pricing_request


def mock_success_task_result(
        **kwargs):
    """mock_success_task_result

    :param kwargs: keyword args dict
    """
    res = kwargs
    res['result']['status'] = SUCCESS
    res['result']['err'] = None
    return res
# end of mock_success_task_result


def mock_err_task_result(
        **kwargs):
    """mock_err_task_result

    :param kwargs: keyword args dict
    """
    res = kwargs
    res['result']['status'] = ERR
    res['result']['err'] = 'test exception'
    return res
# end of mock_err_task_result


class TestPublishPricing(BaseTestCase):
    """TestPublishPricing"""

    @mock.patch(
        'pinance.Pinance',
        new=tests.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.get_pricing.'
         'get_options'),
        new=tests.mock_pinance.mock_get_options)
    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_success_publish_prices(self):
        """test_success_publish_prices"""

        work = build_get_new_pricing_request()
        res = run_get_new_pricing_data(
            work)
        self.assertTrue(
            res['status'] == TESTING_TRAVIS_ERRORS)
        self.assertTrue(
            res['err'] is None)
        self.assertIsNotNone(
            res['rec']['news'])
        self.assertTrue(
            len(res['rec']['news']) == 2)
        self.assertTrue(
            res['rec']['pricing']['close'] == 287.6)
        self.assertTrue(
            res['rec']['options'][0]['strike'] == 286.0)
    # end of test_success_publish_prices

    @mock.patch(
        'pinance.Pinance',
        new=tests.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_err_task_result)
    def test_err_publish_prices(self):
        """test_err_publish_prices"""
        work = build_get_new_pricing_request()
        res = run_get_new_pricing_data(
            work)
        self.assertTrue(
            res['status'] == ERR)
    # end of test_err_publish_prices

# end of TestPublishPricing
