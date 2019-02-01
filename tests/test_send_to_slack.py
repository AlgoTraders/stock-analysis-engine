"""
Test file for:
update prices
"""

import mock
import os
import matplotlib.pyplot as plt
from types import SimpleNamespace
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import FAILED
from analysis_engine.send_to_slack import post_failure
from analysis_engine.send_to_slack import post_message
from analysis_engine.send_to_slack import post_success
from analysis_engine.send_to_slack import post_plot


def mock_request_success_result(url, data=None, params=None, files=None):
    """mock_request_success_result

    :param kwargs: keyword args dict
    """
    res = {'status_code': 200}
    return SimpleNamespace(**res)
# end of mock_request_success_result


def mock_request_failure_result(url, data=None, params=None, files=None):
    """mock_request_failure_result

    :param kwargs: keyword args dict
    """
    res = {'status_code': 400}
    return SimpleNamespace(**res)
# end of mock_request_failure_result


class TestSendToSlack(BaseTestCase):
    """TestSendToSlack"""

    backupWebhook = None
    backupAccessToken = None
    backupChannels = None

    def setUp(self):
        """setUp"""
        if os.getenv('SLACK_WEBHOOK'):
            self.backupWebhook = os.getenv('SLACK_WEBHOOK')
        os.environ['SLACK_WEBHOOK'] = 'https://test.com'
        if os.getenv('SLACK_ACCESS_TOKEN'):
            self.backupWebhook = os.getenv('SLACK_ACCESS_TOKEN')
        os.environ['SLACK_ACCESS_TOKEN'] = 'test_access_token'
        if os.getenv('SLACK_PUBLISH_PLOT_CHANNELS'):
            self.backupWebhook = os.getenv('SLACK_PUBLISH_PLOT_CHANNELS')
        os.environ['SLACK_PUBLISH_PLOT_CHANNELS'] = 'general'
    # end of setUp

    def tearDown(self):
        """tearDown"""
        if self.backupWebhook:
            os.environ['SLACK_WEBHOOK'] = self.backupWebhook
            self.backupWebhook = None
        else:
            os.environ.pop('SLACK_WEBHOOK', None)

        if self.backupAccessToken:
            os.environ['SLACK_ACCESS_TOKEN'] = self.backupAccessToken
            self.backupAccessToken = None
        else:
            os.environ.pop('SLACK_ACCESS_TOKEN', None)

        if self.backupChannels:
            os.environ['SLACK_PUBLISH_PLOT_CHANNELS'] = self.backupChannels
            self.backupChannels = None
        else:
            os.environ.pop('SLACK_PUBLISH_PLOT_CHANNELS', None)
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
    # end of test_post_success_send_to_slack_string_failure

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

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_jupyter(self):
        """test_post_success_send_to_slack_string_success_jupyter"""
        res = post_success('test', jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_jupyter(self):
        """test_post_success_send_to_slack_string_failure_jupyter"""
        res = post_success('test', jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_jupyter(self):
        """test_post_failure_send_to_slack_string_success_jupyter"""
        res = post_failure('test', jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_jupyter(self):
        """test_post_failure_send_to_slack_string_failure_jupyter"""
        res = post_failure('test', jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_jupyter(self):
        """test_post_message_send_to_slack_string_success_jupyter"""
        res = post_message('test', jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_jupyter(self):
        """test_post_message_send_to_slack_string_failure_jupyter"""
        res = post_message('test', jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_jupyter(self):
        """test_post_success_send_to_slack_dict_success_jupyter"""
        res = post_success({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_jupyter(self):
        """test_post_success_send_to_slack_dict_failure_jupyter"""
        res = post_success({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_jupyter(self):
        """test_post_failure_send_to_slack_dict_success_jupyter"""
        res = post_failure({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_jupyter(self):
        """test_post_failure_send_to_slack_dict_failure_jupyter"""
        res = post_failure({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_jupyter(self):
        """test_post_message_send_to_slack_dict_success_jupyter"""
        res = post_message({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_jupyter(self):
        """test_post_message_send_to_slack_dict_failure_jupyter"""
        res = post_message({'test': 'value'}, jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_jupyter(self):
        """test_post_success_send_to_slack_list_success_jupyter"""
        res = post_success(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_jupyter(self):
        """test_post_success_send_to_slack_list_failure_jupyter"""
        res = post_success(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_jupyter(self):
        """test_post_failure_send_to_slack_list_success_jupyter"""
        res = post_failure(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_jupyter(self):
        """test_post_failure_send_to_slack_list_failure_jupyter"""
        res = post_failure(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_jupyter(self):
        """test_post_message_send_to_slack_list_success_jupyter"""
        res = post_message(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_jupyter(self):
        """test_post_message_send_to_slack_list_failure_jupyter"""
        res = post_message(['test', 'test 2'], jupyter=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_jupyter

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_block(self):
        """test_post_success_send_to_slack_string_success_block"""
        res = post_success('test', block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_block(self):
        """test_post_success_send_to_slack_string_failure_block"""
        res = post_success('test', block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_block(self):
        """test_post_failure_send_to_slack_string_success_block"""
        res = post_failure('test', block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_block(self):
        """test_post_failure_send_to_slack_string_failure_block"""
        res = post_failure('test', block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_block(self):
        """test_post_message_send_to_slack_string_success_block"""
        res = post_message('test', block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_block(self):
        """test_post_message_send_to_slack_string_failure_block"""
        res = post_message('test', block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_block(self):
        """test_post_success_send_to_slack_dict_success_block"""
        res = post_success({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_block(self):
        """test_post_success_send_to_slack_dict_failure_block"""
        res = post_success({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_block(self):
        """test_post_failure_send_to_slack_dict_success_block"""
        res = post_failure({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_block(self):
        """test_post_failure_send_to_slack_dict_failure_block"""
        res = post_failure({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_block(self):
        """test_post_message_send_to_slack_dict_success_block"""
        res = post_message({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_block(self):
        """test_post_message_send_to_slack_dict_failure_block"""
        res = post_message({'test': 'value'}, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_block(self):
        """test_post_success_send_to_slack_list_success_block"""
        res = post_success(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_block(self):
        """test_post_success_send_to_slack_list_failure_block"""
        res = post_success(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_block(self):
        """test_post_failure_send_to_slack_list_success_block"""
        res = post_failure(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_block(self):
        """test_post_failure_send_to_slack_list_failure_block"""
        res = post_failure(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_block(self):
        """test_post_message_send_to_slack_list_success_block"""
        res = post_message(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_block(self):
        """test_post_message_send_to_slack_list_failure_block"""
        res = post_message(['test', 'test 2'], block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_width(self):
        """test_post_success_send_to_slack_string_success_width"""
        res = post_success('test', full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_width(self):
        """test_post_success_send_to_slack_string_failure_width"""
        res = post_success('test', full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_width(self):
        """test_post_failure_send_to_slack_string_success_width"""
        res = post_failure('test', full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_width(self):
        """test_post_failure_send_to_slack_string_failure_width"""
        res = post_failure('test', full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_width(self):
        """test_post_message_send_to_slack_string_success_width"""
        res = post_message('test', full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_width(self):
        """test_post_message_send_to_slack_string_failure_width"""
        res = post_message('test', full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_width(self):
        """test_post_success_send_to_slack_dict_success_width"""
        res = post_success({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_width(self):
        """test_post_success_send_to_slack_dict_failure_width"""
        res = post_success({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_width(self):
        """test_post_failure_send_to_slack_dict_success_width"""
        res = post_failure({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_width(self):
        """test_post_failure_send_to_slack_dict_failure_width"""
        res = post_failure({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_width(self):
        """test_post_message_send_to_slack_dict_success_width"""
        res = post_message({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_width(self):
        """test_post_message_send_to_slack_dict_failure_width"""
        res = post_message({'test': 'value'}, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_width(self):
        """test_post_success_send_to_slack_list_success_width"""
        res = post_success(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_width(self):
        """test_post_success_send_to_slack_list_failure_width"""
        res = post_success(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_width(self):
        """test_post_failure_send_to_slack_list_success_width"""
        res = post_failure(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_width(self):
        """test_post_failure_send_to_slack_list_failure_width"""
        res = post_failure(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_width(self):
        """test_post_message_send_to_slack_list_success_width"""
        res = post_message(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_width(self):
        """test_post_message_send_to_slack_list_failure_width"""
        res = post_message(['test', 'test 2'], full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_jupyter_block(self):
        """test_post_success_send_to_slack_string_success_jupyter_block"""
        res = post_success('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_jupyter_block(self):
        """test_post_success_send_to_slack_string_failure_jupyter_block"""
        res = post_success('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_jupyter_block(self):
        """test_post_failure_send_to_slack_string_success_jupyter_block"""
        res = post_failure('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_jupyter_block(self):
        """test_post_failure_send_to_slack_string_failure_jupyter_block"""
        res = post_failure('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_jupyter_block(self):
        """test_post_message_send_to_slack_string_success_jupyter_block"""
        res = post_message('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_jupyter_block(self):
        """test_post_message_send_to_slack_string_failure_jupyter_block"""
        res = post_message('test', jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_jupyter_block(self):
        """test_post_success_send_to_slack_dict_success_jupyter_block"""
        res = post_success({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_jupyter_block(self):
        """test_post_success_send_to_slack_dict_failure_jupyter_block"""
        res = post_success({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_jupyter_block(self):
        """test_post_failure_send_to_slack_dict_success_jupyter_block"""
        res = post_failure({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_jupyter_block(self):
        """test_post_failure_send_to_slack_dict_failure_jupyter_block"""
        res = post_failure({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_jupyter_block(self):
        """test_post_message_send_to_slack_dict_success_jupyter_block"""
        res = post_message({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_jupyter_block(self):
        """test_post_message_send_to_slack_dict_failure_jupyter_block"""
        res = post_message({'test': 'value'}, jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_jupyter_block(self):
        """test_post_success_send_to_slack_list_success_jupyter_block"""
        res = post_success(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_jupyter_block(self):
        """test_post_success_send_to_slack_list_failure_jupyter_block"""
        res = post_success(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_jupyter_block(self):
        """test_post_failure_send_to_slack_list_success_jupyter_block"""
        res = post_failure(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_jupyter_block(self):
        """test_post_failure_send_to_slack_list_failure_jupyter_block"""
        res = post_failure(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_jupyter_block(self):
        """test_post_message_send_to_slack_list_success_jupyter_block"""
        res = post_message(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_jupyter_block(self):
        """test_post_message_send_to_slack_list_failure_jupyter_block"""
        res = post_message(['test', 'test 2'], jupyter=True, block=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_jupyter_block

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_jupyter_width(self):
        """test_post_success_send_to_slack_string_success_jupyter_width"""
        res = post_success('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_jupyter_width(self):
        """test_post_success_send_to_slack_string_failure_jupyter_width"""
        res = post_success('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_jupyter_width(self):
        """test_post_failure_send_to_slack_string_success_jupyter_width"""
        res = post_failure('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_jupyter_width(self):
        """test_post_failure_send_to_slack_string_failure_jupyter_width"""
        res = post_failure('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_jupyter_width(self):
        """test_post_message_send_to_slack_string_success_jupyter_width"""
        res = post_message('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_jupyter_width(self):
        """test_post_message_send_to_slack_string_failure_jupyter_width"""
        res = post_message('test', jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_jupyter_width(self):
        """test_post_success_send_to_slack_dict_success_jupyter_width"""
        res = post_success({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_jupyter_width(self):
        """test_post_success_send_to_slack_dict_failure_jupyter_width"""
        res = post_success({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_jupyter_width(self):
        """test_post_failure_send_to_slack_dict_success_jupyter_width"""
        res = post_failure({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_jupyter_width(self):
        """test_post_failure_send_to_slack_dict_failure_jupyter_width"""
        res = post_failure({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_jupyter_width(self):
        """test_post_message_send_to_slack_dict_success_jupyter_width"""
        res = post_message({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_jupyter_width(self):
        """test_post_message_send_to_slack_dict_failure_jupyter_width"""
        res = post_message({'test': 'value'}, jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_jupyter_width(self):
        """test_post_success_send_to_slack_list_success_jupyter_width"""
        res = post_success(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_jupyter_width(self):
        """test_post_success_send_to_slack_list_failure_jupyter_width"""
        res = post_success(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_jupyter_width(self):
        """test_post_failure_send_to_slack_list_success_jupyter_width"""
        res = post_failure(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_jupyter_width(self):
        """test_post_failure_send_to_slack_list_failure_jupyter_width"""
        res = post_failure(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_jupyter_width(self):
        """test_post_message_send_to_slack_list_success_jupyter_width"""
        res = post_message(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_jupyter_width(self):
        """test_post_message_send_to_slack_list_failure_jupyter_width"""
        res = post_message(['test', 'test 2'], jupyter=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_jupyter_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_block_width(self):
        """test_post_success_send_to_slack_string_success_block_width"""
        res = post_success('test', block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_block_width(self):
        """test_post_success_send_to_slack_string_failure_block_width"""
        res = post_success('test', block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_block_width(self):
        """test_post_failure_send_to_slack_string_success_block_width"""
        res = post_failure('test', block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_block_width(self):
        """test_post_failure_send_to_slack_string_failure_block_width"""
        res = post_failure('test', block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_block_width(self):
        """test_post_message_send_to_slack_string_success_block_width"""
        res = post_message('test', block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_block_width(self):
        """test_post_message_send_to_slack_string_failure_block_width"""
        res = post_message('test', block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_block_width(self):
        """test_post_success_send_to_slack_dict_success_block_width"""
        res = post_success({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_block_width(self):
        """test_post_success_send_to_slack_dict_failure_block_width"""
        res = post_success({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_block_width(self):
        """test_post_failure_send_to_slack_dict_success_block_width"""
        res = post_failure({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_block_width(self):
        """test_post_failure_send_to_slack_dict_failure_block_width"""
        res = post_failure({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_block_width(self):
        """test_post_message_send_to_slack_dict_success_block_width"""
        res = post_message({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_block_width(self):
        """test_post_message_send_to_slack_dict_failure_block_width"""
        res = post_message({'test': 'value'}, block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_block_width(self):
        """test_post_success_send_to_slack_list_success_block_width"""
        res = post_success(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_block_width(self):
        """test_post_success_send_to_slack_list_failure_block_width"""
        res = post_success(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_block_width(self):
        """test_post_failure_send_to_slack_list_success_block_width"""
        res = post_failure(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_block_width(self):
        """test_post_failure_send_to_slack_list_failure_block_width"""
        res = post_failure(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_block_width(self):
        """test_post_message_send_to_slack_list_success_block_width"""
        res = post_message(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_block_width(self):
        """test_post_message_send_to_slack_list_failure_block_width"""
        res = post_message(['test', 'test 2'], block=True, full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_block_width

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_string_success_all(self):
        """test_post_success_send_to_slack_string_success_all"""
        res = post_success('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_string_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_string_failure_all(self):
        """test_post_success_send_to_slack_string_failure_all"""
        res = post_success('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_string_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_string_success_all(self):
        """test_post_failure_send_to_slack_string_success_all"""
        res = post_failure('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_string_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_string_failure_all(self):
        """test_post_failure_send_to_slack_string_failure_all"""
        res = post_failure('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_string_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_string_success_all(self):
        """test_post_message_send_to_slack_string_success_all"""
        res = post_message('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_string_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_string_failure_all(self):
        """test_post_message_send_to_slack_string_failure_all"""
        res = post_message('test',
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_string_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_dict_success_all(self):
        """test_post_success_send_to_slack_dict_success_all"""
        res = post_success({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_dict_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_dict_failure_all(self):
        """test_post_success_send_to_slack_dict_failure_all"""
        res = post_success({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_dict_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_dict_success_all(self):
        """test_post_failure_send_to_slack_dict_success_all"""
        res = post_failure({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_dict_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_dict_failure_all(self):
        """test_post_failure_send_to_slack_dict_failure_all"""
        res = post_failure({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_dict_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_dict_success_all(self):
        """test_post_message_send_to_slack_dict_success_all"""
        res = post_message({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_dict_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_dict_failure_all(self):
        """test_post_message_send_to_slack_dict_failure_all"""
        res = post_message({'test': 'value'},
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_dict_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_success_send_to_slack_list_success_all(self):
        """test_post_success_send_to_slack_list_success_all"""
        res = post_success(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_success_send_to_slack_list_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_success_send_to_slack_list_failure_all(self):
        """test_post_success_send_to_slack_list_failure_all"""
        res = post_success(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_success_send_to_slack_list_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_failure_send_to_slack_list_success_all(self):
        """test_post_failure_send_to_slack_list_success_all"""
        res = post_failure(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_failure_send_to_slack_list_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_failure_send_to_slack_list_failure_all(self):
        """test_post_failure_send_to_slack_list_failure_all"""
        res = post_failure(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_failure_send_to_slack_list_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_message_send_to_slack_list_success_all(self):
        """test_post_message_send_to_slack_list_success_all"""
        res = post_message(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_message_send_to_slack_list_success_all

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_message_send_to_slack_list_failure_all(self):
        """test_post_message_send_to_slack_list_failure_all"""
        res = post_message(['test', 'test 2'],
                           jupyter=True,
                           block=True,
                           full_width=True)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_message_send_to_slack_list_failure_all

    @mock.patch(
        'requests.post',
        new=mock_request_success_result)
    def test_post_plot_send_to_slack_success(self):
        """test_post_plot_send_to_slack_success"""
        res = post_plot(plt)
        self.assertTrue(res['status'] == SUCCESS)
    # end of test_post_plot_send_to_slack_success

    @mock.patch(
        'requests.post',
        new=mock_request_failure_result)
    def test_post_plot_send_to_slack_failure(self):
        """test_post_plot_send_to_slack_failure"""
        res = post_plot(plt)
        self.assertTrue(res['status'] == FAILED)
    # end of test_post_plot_send_to_slack_failure

# end of TestSendToSlack
