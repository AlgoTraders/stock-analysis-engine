"""

Test file for - update prices
=============================

Integration Tests
-----------------

Please ensure ``redis`` and ``minio`` are running and export this:

::

    export INT_TESTS=1

"""

import os
import mock
import tests.mock_pinance
import tests.mock_boto3_s3
import tests.mock_redis
from tests.base_test import BaseTestCase
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ERR
from analysis_engine.consts import S3_ACCESS_KEY
from analysis_engine.consts import S3_SECRET_KEY
from analysis_engine.consts import S3_REGION_NAME
from analysis_engine.consts import S3_ADDRESS
from analysis_engine.consts import S3_SECURE
from analysis_engine.consts import REDIS_ADDRESS
from analysis_engine.consts import REDIS_KEY
from analysis_engine.consts import REDIS_PASSWORD
from analysis_engine.consts import REDIS_DB
from analysis_engine.consts import REDIS_EXPIRE
from analysis_engine.consts import ev
from analysis_engine.work_tasks.publish_pricing_update \
    import run_publish_pricing_update
from analysis_engine.api_requests \
    import build_publish_pricing_request


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


class TestPublishPricingData(BaseTestCase):
    """TestPublishPricingData"""

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
    def test_success_publish_pricing_data(self):
        """test_success_publish_pricing_data"""
        work = build_publish_pricing_request()
        res = run_publish_pricing_update(
            work)
        self.assertTrue(
            res['status'] == SUCCESS)
        self.assertTrue(
            res['err'] is None)
        self.assertTrue(
            res['rec'] is not None)
        record = res['rec']
        self.assertEqual(
            record['ticker'],
            TICKER)
        self.assertEqual(
            record['s3_enabled'],
            False)
        self.assertEqual(
            record['redis_enabled'],
            False)
        self.assertEqual(
            record['s3_bucket'],
            work['s3_bucket'])
        self.assertEqual(
            record['s3_key'],
            work['s3_key'])
        self.assertEqual(
            record['redis_key'],
            work['redis_key'])
    # end of test_success_publish_pricing_data

    def test_err_publish_pricing_data(self):
        """test_err_publish_pricing_data"""
        work = build_publish_pricing_request()
        work['ticker'] = None
        res = run_publish_pricing_update(
            work)
        self.assertTrue(
            res['status'] == ERR)
        self.assertTrue(
            res['err'] == 'missing ticker')
    # end of test_err_publish_pricing_data

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
    @mock.patch(
        ('boto3.resource'),
        new=tests.mock_boto3_s3.build_boto3_resource)
    def test_success_s3_upload(self):
        """test_success_s3_upload"""
        work = build_publish_pricing_request()
        work['s3_enabled'] = 1
        work['redis_enabled'] = 0
        work['s3_access_key'] = S3_ACCESS_KEY
        work['s3_secret_key'] = S3_SECRET_KEY
        work['s3_region_name'] = S3_REGION_NAME
        work['s3_address'] = S3_ADDRESS
        work['s3_secure'] = S3_SECURE
        res = run_publish_pricing_update(
            work)
        self.assertTrue(
            res['status'] == SUCCESS)
    # end of test_success_s3_upload

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
    @mock.patch(
        ('redis.Redis'),
        new=tests.mock_redis.MockRedis)
    def test_success_redis_set(self):
        """test_success_redis_set"""
        work = build_publish_pricing_request()
        work['s3_enabled'] = 0
        work['redis_enabled'] = 1
        work['redis_address'] = REDIS_ADDRESS
        work['redis_db'] = REDIS_DB
        work['redis_key'] = REDIS_KEY
        work['redis_password'] = REDIS_PASSWORD
        work['redis_expire'] = REDIS_EXPIRE
        res = run_publish_pricing_update(
            work)
        self.assertTrue(
            res['status'] == SUCCESS)
    # end of test_success_redis_set

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

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
    def test_integration_s3_upload(self):
        """test_integration_s3_upload"""
        if ev('INT_TESTS', '0') == '1':
            work = build_publish_pricing_request()
            work['s3_enabled'] = 1
            work['redis_enabled'] = 0
            work['s3_access_key'] = S3_ACCESS_KEY
            work['s3_secret_key'] = S3_SECRET_KEY
            work['s3_region_name'] = S3_REGION_NAME
            work['s3_address'] = S3_ADDRESS
            work['s3_secure'] = S3_SECURE
            work['s3_bucket'] = 'integration-tests'
            work['s3_key'] = 'integration-test-v1'
            work['redis_key'] = 'integration-test-v1'
            os.environ.pop('AWS_DEFAULT_PROFILE', None)
            res = run_publish_pricing_update(
                work)
            self.assertTrue(
                res['status'] == SUCCESS)
    # end of test_integration_s3_upload

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
    def test_integration_redis_set(self):
        """test_integration_redis_set"""
        if ev('INT_TESTS', '0') == '1':
            work = build_publish_pricing_request()
            work['s3_enabled'] = 0
            work['redis_enabled'] = 1
            work['redis_address'] = REDIS_ADDRESS
            work['redis_db'] = REDIS_DB
            work['redis_key'] = REDIS_KEY
            work['redis_password'] = REDIS_PASSWORD
            work['redis_expire'] = REDIS_EXPIRE
            work['redis_key'] = 'integration-test-v1'
            work['s3_key'] = 'integration-test-v1'
            res = run_publish_pricing_update(
                work)
            self.assertTrue(
                res['status'] == SUCCESS)
    # end of test_integration_redis_set

# end of TestPublishPricingData
