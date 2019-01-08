"""
Test file for:
update prices
"""

import mock
import analysis_engine.mocks.mock_pinance
import analysis_engine.mocks.mock_iex
from analysis_engine.mocks.base_test import BaseTestCase
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


def mock_success_iex_fetch(
        **kwargs):
    """mock_success_iex_fetch

    :param kwargs: keyword args dict
    """
    res = {
        'status': SUCCESS,
        'err': None,
        'rec': {
            'data': kwargs
        }
    }
    return res
# end of mock_success_iex_fetch


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

    :param kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_exception_run_publish_pricing_update')
# end of mock_exception_run_publish_pricing_update


def mock_error_iex_fetch(
        **kwargs):
    """mock_error_iex_fetch

    :param kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_error_iex_fetch')
# end of mock_error_iex_fetch


class TestGetNewPricing(BaseTestCase):
    """TestGetNewPricing"""

    @mock.patch(
        'pinance.Pinance',
        new=analysis_engine.mocks.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.iex.get_data.'
         'get_data_from_iex'),
        new=mock_success_iex_fetch)
    @mock.patch(
        ('analysis_engine.get_pricing.'
         'get_options'),
        new=analysis_engine.mocks.mock_pinance.mock_get_options)
    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_success_get_new_pricing(self):
        """test_success_get_new_pricing"""
        # yahoo is disabled
        return 0
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
            len(res['rec']['news']) >= 1)
        self.assertTrue(
            len(res['rec']['pricing']) >= 1)
        self.assertTrue(
            len(res['rec']['options']) >= 1)
    # end of test_success_get_new_pricing

    @mock.patch(
        'pinance.Pinance',
        new=analysis_engine.mocks.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.iex.get_data.'
         'get_data_from_iex'),
        new=mock_success_iex_fetch)
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

    @mock.patch(
        ('analysis_engine.iex.get_data.'
         'get_data_from_iex'),
        new=mock_error_iex_fetch)
    @mock.patch(
        'pinance.Pinance',
        new=analysis_engine.mocks.mock_pinance.MockPinance)
    @mock.patch(
        ('analysis_engine.get_pricing.'
         'get_options'),
        new=analysis_engine.mocks.mock_pinance.mock_get_options)
    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_success_if_iex_errors(self):
        """test_success_if_iex_errors"""
        work = build_get_new_pricing_request()
        work['label'] = 'test_success_if_iex_errors'
        res = run_get_new_pricing_data(
            work)
        self.assertTrue(
            res['status'] == SUCCESS)
    # end of test_success_if_iex_errors

# end of TestGetNewPricing
