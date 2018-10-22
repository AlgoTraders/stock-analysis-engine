"""

Test file for - publish ticker aggregate from s3 to redis
=========================================================

Integration Tests
-----------------

Please ensure ``redis`` and ``minio`` are running and export this:

::

    export INT_TESTS=1

"""

import json
import mock
import analysis_engine.mocks.mock_boto3_s3
import analysis_engine.mocks.mock_redis
from analysis_engine.mocks.base_test import BaseTestCase
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
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ERR
from analysis_engine.consts import ev
from analysis_engine.api_requests \
    import build_cache_ready_pricing_dataset
from analysis_engine.work_tasks.publish_ticker_aggregate_from_s3 \
    import run_publish_ticker_aggregate_from_s3
from analysis_engine.api_requests \
    import build_publish_ticker_aggregate_from_s3_request
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def mock_success_task_result(
        **kwargs):
    """mock_success_task_result

    :param kwargs: keyword args dict
    """
    log.info('MOCK - mock_success_task_result')
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
    log.info('MOCK - mock_err_task_result')
    res = kwargs
    res['result']['status'] = ERR
    res['result']['err'] = 'test exception'
    return res
# end of mock_err_task_result


def mock_s3_read_contents_from_key(
        s3,
        s3_bucket_name,
        s3_key,
        encoding='utf-8',
        convert_as_json=True):
    """mock_s3_read_contents_from_key

    Download the S3 key contents as a string. This
    will raise exceptions.

    :param s3_obj: existing S3 object
    :param s3_bucket_name: bucket name
    :param s3_key: S3 key
    :param encoding: utf-8 by default
    :param convert_to_json: auto-convert to a dict
    """
    log.info('MOCK - mock_s3_read_contents_from_key')
    data = build_cache_ready_pricing_dataset()
    if not convert_as_json:
        data = json.dumps(data)
    return data
# end of mock_s3_read_contents_from_key


class TestPublishTickerAggregateFromS3(BaseTestCase):
    """TestPublishTickerAggregateFromS3"""

    @mock.patch(
        ('boto3.resource'),
        new=analysis_engine.mocks.mock_boto3_s3.build_boto3_resource)
    @mock.patch(
        ('redis.Redis'),
        new=analysis_engine.mocks.mock_redis.MockRedis)
    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    def test_success_publish_ticker_aggregate_from_s3(self):
        """test_success_publish_ticker_aggregate_from_s3"""
        work = build_publish_ticker_aggregate_from_s3_request()
        work['s3_read_enabled'] = 1
        work['s3_upload_enabled'] = 1
        work['redis_enabled'] = 1
        work['s3_access_key'] = S3_ACCESS_KEY
        work['s3_secret_key'] = S3_SECRET_KEY
        work['s3_region_name'] = S3_REGION_NAME
        work['s3_address'] = S3_ADDRESS
        work['s3_secure'] = S3_SECURE
        work['redis_address'] = REDIS_ADDRESS
        work['redis_db'] = REDIS_DB
        work['redis_key'] = REDIS_KEY
        work['redis_password'] = REDIS_PASSWORD
        work['redis_expire'] = REDIS_EXPIRE
        work['s3_bucket'] = 'integration-tests'
        work['s3_key'] = 'integration-test-v1'
        work['redis_key'] = 'integration-test-v1'

        res = run_publish_ticker_aggregate_from_s3(
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
            record['s3_read_enabled'],
            True)
        self.assertEqual(
            record['s3_upload_enabled'],
            True)
        self.assertEqual(
            record['redis_enabled'],
            True)
        self.assertEqual(
            record['s3_bucket'],
            work['s3_bucket'])
        self.assertEqual(
            record['s3_key'],
            work['s3_key'])
        self.assertEqual(
            record['redis_key'],
            work['redis_key'])
    # end of test_success_publish_ticker_aggregate_from_s3

    def test_err_publish_ticker_aggregate_from_s3(self):
        """test_err_publish_ticker_aggregate_from_s3"""
        work = build_publish_ticker_aggregate_from_s3_request()
        work['ticker'] = None
        res = run_publish_ticker_aggregate_from_s3(
            work)
        self.assertTrue(
            res['status'] == ERR)
        self.assertTrue(
            res['err'] == 'missing ticker')
    # end of test_err_publish_ticker_aggregate_from_s3

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_integration_publish_ticker_aggregate_from_s3(self):
        """test_integration_publish_ticker_aggregate_from_s3"""
        if ev('INT_TESTS', '0') == '0':
            return

        work = build_publish_ticker_aggregate_from_s3_request()
        work['s3_read_enabled'] = 1
        work['s3_upload_enabled'] = 1
        work['redis_enabled'] = 1
        work['s3_access_key'] = S3_ACCESS_KEY
        work['s3_secret_key'] = S3_SECRET_KEY
        work['s3_region_name'] = S3_REGION_NAME
        work['s3_address'] = S3_ADDRESS
        work['s3_secure'] = S3_SECURE
        work['redis_address'] = REDIS_ADDRESS
        work['redis_db'] = REDIS_DB
        work['redis_key'] = REDIS_KEY
        work['redis_password'] = REDIS_PASSWORD
        work['redis_expire'] = REDIS_EXPIRE
        work['s3_bucket'] = 'integration-tests'
        work['s3_key'] = 'integration-test-v1'
        work['redis_key'] = 'integration-test-v1'

        res = run_publish_ticker_aggregate_from_s3(
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
            record['s3_read_enabled'],
            True)
        self.assertEqual(
            record['s3_upload_enabled'],
            True)
        self.assertEqual(
            record['redis_enabled'],
            True)
        self.assertEqual(
            record['s3_bucket'],
            work['s3_bucket'])
        self.assertEqual(
            record['s3_key'],
            work['s3_key'])
        self.assertEqual(
            record['redis_key'],
            work['redis_key'])
    # end of test_integration_publish_ticker_aggregate_from_s3

    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_integration_publish_ticker_aggregate_from_s3_to_redis(self):
        """test_integration_publish_ticker_aggregate_from_s3_to_redis"""
        if ev('INT_TESTS', '0') == '0':
            return

        work = build_publish_ticker_aggregate_from_s3_request()
        work['s3_read_enabled'] = 1
        work['s3_upload_enabled'] = 0
        work['redis_enabled'] = 1
        work['s3_access_key'] = S3_ACCESS_KEY
        work['s3_secret_key'] = S3_SECRET_KEY
        work['s3_region_name'] = S3_REGION_NAME
        work['s3_address'] = S3_ADDRESS
        work['s3_secure'] = S3_SECURE
        work['redis_address'] = REDIS_ADDRESS
        work['redis_db'] = REDIS_DB
        work['redis_key'] = REDIS_KEY
        work['redis_password'] = REDIS_PASSWORD
        work['redis_expire'] = REDIS_EXPIRE
        work['s3_bucket'] = 'integration-tests'
        work['s3_key'] = 'integration-test-v1'
        work['redis_key'] = 'integration-test-v1'

        res = run_publish_ticker_aggregate_from_s3(
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
            record['s3_read_enabled'],
            True)
        self.assertEqual(
            record['s3_upload_enabled'],
            False)
        self.assertEqual(
            record['redis_enabled'],
            True)
        self.assertEqual(
            record['s3_bucket'],
            work['s3_bucket'])
        self.assertEqual(
            record['s3_key'],
            work['s3_key'])
        self.assertEqual(
            record['redis_key'],
            work['redis_key'])
    # end of test_integration_publish_ticker_aggregate_from_s3_to_redis

    @mock.patch(
        ('analysis_engine.get_task_results.'
         'get_task_results'),
        new=mock_success_task_result)
    def test_integration_publish_ticker_aggregate_from_s3_to_s3(self):
        """test_integration_publish_ticker_aggregate_from_s3_to_s3"""
        if ev('INT_TESTS', '0') == '0':
            return

        work = build_publish_ticker_aggregate_from_s3_request()
        work['s3_read_enabled'] = 1
        work['s3_upload_enabled'] = 1
        work['redis_enabled'] = 0
        work['s3_access_key'] = S3_ACCESS_KEY
        work['s3_secret_key'] = S3_SECRET_KEY
        work['s3_region_name'] = S3_REGION_NAME
        work['s3_address'] = S3_ADDRESS
        work['s3_secure'] = S3_SECURE
        work['redis_address'] = REDIS_ADDRESS
        work['redis_db'] = REDIS_DB
        work['redis_key'] = REDIS_KEY
        work['redis_password'] = REDIS_PASSWORD
        work['redis_expire'] = REDIS_EXPIRE
        work['s3_bucket'] = 'integration-tests'
        work['s3_key'] = 'integration-test-v1'
        work['redis_key'] = 'integration-test-v1'

        res = run_publish_ticker_aggregate_from_s3(
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
            record['s3_read_enabled'],
            True)
        self.assertEqual(
            record['s3_upload_enabled'],
            True)
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
    # end of test_integration_publish_ticker_aggregate_from_s3_to_s3

# end of TestPublishTickerAggregateFromS3
