"""
Test file for:
update prices
"""

import mock
import os
from types import SimpleNamespace
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import FAILED
from analysis_engine.send_to_slack import post_failure
from analysis_engine.send_to_slack import post_message
from analysis_engine.send_to_slack import post_success


def mock_request_success_result(url, data):
    """mock_request_success_result

    :param kwargs: keyword args dict
    """
    res = {'status_code': 200}
    return SimpleNamespace(**res)
# end of mock_request_success_result


def mock_request_failure_result(url, data):
    """mock_request_failure_result

    :param kwargs: keyword args dict
    """
    res = {'status_code': 400}
    return SimpleNamespace(**res)
# end of mock_request_failure_result


class TestSendToSlack(BaseTestCase):
    """TestSendToSlack"""

    backupWebhook = None

    def setUp(self):
        """setUp"""
        if os.getenv('SLACK_WEBHOOK'):
            self.backupWebhook = os.getenv('SLACK_WEBHOOK')
        os.environ['SLACK_WEBHOOK'] = 'https://test.com'
    # end of setUp

    def tearDown(self):
        """tearDown"""
        if self.backupWebhook:
            os.environ['SLACK_WEBHOOK'] = self.backupWebhook
            self.backupWebhook = None
        else:
            os.environ.pop('SLACK_WEBHOOK', None)
    # end of tearDown

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success(self):
        """test_post_success_send_to_slack_string_success"""
        res = post_success('test')
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure(self):
        """test_post_success_send_to_slack_string_failure"""
        res = post_success('test')
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_success

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success(self):
        """test_post_failure_send_to_slack_string_success"""
        res = post_failure('test')
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure(self):
        """test_post_failure_send_to_slack_string_failure"""
        res = post_failure('test')
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success(self):
        """test_post_message_send_to_slack_string_success"""
        res = post_message('test')
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure(self):
        """test_post_message_send_to_slack_string_failure"""
        res = post_message('test')
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success(self):
        """test_post_success_send_to_slack_dict_success"""
        res = post_success({'test': 'value'})
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure(self):
        """test_post_success_send_to_slack_dict_failure"""
        res = post_success({'test': 'value'})
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success(self):
        """test_post_failure_send_to_slack_dict_success"""
        res = post_failure({'test': 'value'})
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure(self):
        """test_post_failure_send_to_slack_dict_failure"""
        res = post_failure({'test': 'value'})
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success(self):
        """test_post_message_send_to_slack_dict_success"""
        res = post_message({'test': 'value'})
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure(self):
        """test_post_message_send_to_slack_dict_failure"""
        res = post_message({'test': 'value'})
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success(self):
        """test_post_success_send_to_slack_list_success"""
        res = post_success(['test', 'test 2'])
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure(self):
        """test_post_success_send_to_slack_list_failure"""
        res = post_success(['test', 'test 2'])
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success(self):
        """test_post_failure_send_to_slack_list_success"""
        res = post_failure(['test', 'test 2'])
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure(self):
        """test_post_failure_send_to_slack_list_failure"""
        res = post_failure(['test', 'test 2'])
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success(self):
        """test_post_message_send_to_slack_list_success"""
        res = post_message(['test', 'test 2'])
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure(self):
        """test_post_message_send_to_slack_list_failure"""
        res = post_message(['test', 'test 2'])
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure

# end of TestSendToSlack
