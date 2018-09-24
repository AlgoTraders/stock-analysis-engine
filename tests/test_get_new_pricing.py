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


def mock_exception_run_publish_pricing_update(
        **kwargs):
    """mock_exception_run_publish_pricing_update

    :param **kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_exception_run_publish_pricing_update')
# end of mock_exception_run_publish_pricing_update


class TestGetNewPricing(BaseTestCase):
    """TestGetNewPricing"""

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
    def test_success_get_new_pricing(self):
        """test_success_get_new_pricing"""
        work = build_get_new_pricing_request()
        work['label'] = 'test_success_get_new_pricing'
        res = run_get_new_pricing_data(
            work)
        self.assertTrue(
            res['status'] == SUCCESS)
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
    # end of test_success_get_new_pricing

    @mock.patch(
        'pinance.Pinance',
        new=tests.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_pricing_update.'
         'run_publish_pricing_update'),
        new=mock_exception_run_publish_pricing_update)
    def test_err_get_new_pricing(self):
        """test_err_get_new_pricing"""
        work = build_get_new_pricing_request()
        work['label'] = 'test_err_get_new_pricing'
        res = run_get_new_pricing_data(
            work)
        self.assertTrue(
            res['status'] == ERR)
    # end of test_err_get_new_pricing

# end of TestGetNewPricing
