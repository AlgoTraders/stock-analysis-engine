"""

Test file for - publish from s3 to redis
========================================

Integration Tests
-----------------

Please ensure ``redis`` and ``minio`` are running and export this:

::

    export INT_TESTS=1

"""

import os
import uuid
import json
import mock
from analysis_engine.mocks.mock_boto3_s3 import \
    build_boto3_resource
from analysis_engine.mocks.mock_boto3_s3 import \
    mock_publish_from_s3_to_redis
from analysis_engine.mocks.mock_boto3_s3 import \
    mock_publish_from_s3_to_redis_err
from analysis_engine.mocks.mock_boto3_s3 import \
    mock_publish_from_s3_exception
from analysis_engine.mocks.mock_redis import MockRedis
from analysis_engine.mocks.mock_redis import MockRedisFailToConnect
from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ERR
from analysis_engine.consts import PREPARE_DATA_MIN_SIZE
from analysis_engine.api_requests \
    import build_cache_ready_pricing_dataset
from analysis_engine.work_tasks.prepare_pricing_dataset \
    import run_prepare_pricing_dataset
from analysis_engine.api_requests \
    import build_prepare_dataset_request
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


def mock_exception_run_publish_pricing_update(
        **kwargs):
    """mock_exception_run_publish_pricing_update

    :param kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_exception_run_publish_pricing_update')
# end of mock_exception_run_publish_pricing_update


def mock_redis_get_exception(
        **kwargs):
    """mock_redis_get_exception

    :param kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_redis_get_exception')
# end of mock_redis_get_exception


def mock_flatten_dict_err(
        **kwargs):
    """mock_flatten_dict_err

    :param kwargs: keyword args dict
    """
    raise Exception(
        'test throwing mock_flatten_dict_err')
# end of mock_flatten_dict_err


def mock_flatten_dict_empty(
        **kwags):
    """mock_flatten_dict_empty

    :param kwargs: keyword args dict
    """
    return None
# end of mock_flatten_dict_empty


def mock_redis_get_data_none(
        **kwargs):
    return {
        'status': SUCCESS,
        'err': None,
        'rec': {
            'data': None
        }
    }
# end of mock_redis_get_data_none


def mock_flatten_dict_too_small(
        **kwargs):
    """mock_flatten_dict_too_small

    :param kwargs: keyword args dict
    """
    return '012345678901234567890'[0:PREPARE_DATA_MIN_SIZE-1]
# end of mock_flatten_dict_too_small


class TestPreparePricingDataset(BaseTestCase):
    """TestPreparePricingDataset"""

    def build_test_key(
            self,
            test_name=None):
        """build_test_key

        :param test_name: use this test label name
        """
        use_test_name = test_name
        if not use_test_name:
            use_test_name = str(uuid.uuid4())
        test_key = f'{__name__}_{use_test_name}'
        return test_key
    # end of build_test_key

    # throws on redis client creation
    @mock.patch(
        ('redis.Redis'),
        new=MockRedisFailToConnect)
    def test_redis_connection_exception_prepare_pricing(self):
        """test_redis_connection_exception_prepare_pricing"""
        expected_err = 'test MockRedisFailToConnect'
        redis_key = self.build_test_key(
            test_name='test_redis_connection_exception_prepare_pricing')
        s3_key = redis_key
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_redis_connection_exception_prepare_pricing

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('analysis_engine.get_data_from_redis_key.'
         'get_data_from_redis_key'),
        new=mock_redis_get_exception)
    def test_redis_get_exception_prepare_pricing(self):
        """test_redis_get_exception_prepare_pricing"""
        expected_err = 'test throwing mock_redis_get_exception'
        redis_key = self.build_test_key(
            test_name='test_redis_get_exception_prepare_pricing')
        s3_key = redis_key
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_redis_get_exception_prepare_pricing

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    def test_redis_get_no_data_found_for_prepare_pricing(self):
        """test_redis_get_no_data_found_for_prepare_pricing"""
        expected_err = (
            'did not find any data to prepare in redis_key=')
        test_name = 'test_redis_get_no_data_found_for_prepare_pricing'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        os.environ.pop('TEST_S3_CONTENTS', None)
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_redis_get_no_data_found_for_prepare_pricing

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis_err)
    def test_redis_get_no_data_found_for_prepare_pricing_err(self):
        """test_redis_get_no_data_found_for_prepare_pricing_err"""
        expected_err = (
            'prepare ERR failed loading from bucket')
        test_name = 'test_redis_get_no_data_found_for_prepare_pricing_err'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = {
            'test_name': test_name
        }
        os.environ['TEST_S3_CONTENTS'] = json.dumps(value)
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_redis_get_no_data_found_for_prepare_pricing_err

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    def test_data_invalid_json_to_prepare(self):
        """test_data_invalid_json_to_prepare"""
        test_name = 'test_data_invalid_json_to_prepare'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        expected_err = (
            'prepare did not find any data to prepare in '
            f'redis_key={redis_key}')
        value = {
            'BAD_JSON': test_name
        }
        value_str = json.dumps(value)[0:PREPARE_DATA_MIN_SIZE-1]
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_data_invalid_json_to_prepare

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    def test_data_too_small_to_prepare(self):
        """test_data_too_small_to_prepare"""
        expected_err = (
            'not enough data=')
        test_name = 'test_data_too_small_to_prepare'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = {
            '0': '1'
        }
        value_str = json.dumps(value)[0:PREPARE_DATA_MIN_SIZE-1]
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_data_too_small_to_prepare

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_exception)
    def test_s3_publish_exception(self):
        """test_s3_publish_exception"""
        expected_err = 'test mock_publish_from_s3_exception'
        redis_key = self.build_test_key(
            test_name='test_s3_publish_exception')
        s3_key = redis_key
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_s3_publish_exception

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    @mock.patch(
        ('analysis_engine.dict_to_csv.flatten_dict'),
        new=mock_flatten_dict_err)
    def test_failed_flatten_dict(self):
        """test_failed_flatten_dict"""
        expected_err = (
            'flatten - convert to csv failed with ex=')
        test_name = 'test_failed_flatten_dict'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = self.get_pricing_test_data()
        value_str = json.dumps(value)
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_failed_flatten_dict

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    @mock.patch(
        ('analysis_engine.dict_to_csv.flatten_dict'),
        new=mock_flatten_dict_empty)
    def test_empty_flatten_dict(self):
        """test_empty_flatten_dict"""
        expected_err = (
            'flatten - did not return any data from redis_key=')
        test_name = 'test_empty_flatten_dict'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = self.get_pricing_test_data()
        value_str = json.dumps(value)
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_empty_flatten_dict

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    @mock.patch(
        ('analysis_engine.dict_to_csv.flatten_dict'),
        new=mock_flatten_dict_too_small)
    def test_too_small_flatten_dict(self):
        """test_too_small_flatten_dict"""
        expected_err = (
            'prepare - there is not enough data=')
        test_name = 'test_too_small_flatten_dict'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = self.get_pricing_test_data()
        value_str = json.dumps(value)
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            ERR)
        self.assertTrue(
            expected_err in res['err'])
        self.assertTrue(
            res['rec'] is not None)
    # end of test_too_small_flatten_dict

    # this will mock the redis set and get
    @mock.patch(
        ('redis.Redis'),
        new=MockRedis)
    @mock.patch(
        ('boto3.resource'),
        new=build_boto3_resource)
    @mock.patch(
        ('analysis_engine.s3_read_contents_from_key.'
         's3_read_contents_from_key'),
        new=mock_s3_read_contents_from_key)
    @mock.patch(
        ('analysis_engine.work_tasks.publish_from_s3_to_redis.'
         'publish_from_s3_to_redis'),
        new=mock_publish_from_s3_to_redis)
    def test_prepare_pricing_data_success(self):
        """test_prepare_pricing_data_success"""
        test_name = 'test_prepare_pricing_data_success'
        redis_key = self.build_test_key(
            test_name=test_name)
        s3_key = redis_key
        value = self.get_pricing_test_data()
        value_str = json.dumps(value)
        os.environ['TEST_S3_CONTENTS'] = value_str
        work = build_prepare_dataset_request()
        work['s3_key'] = s3_key
        work['redis_key'] = redis_key
        res = run_prepare_pricing_dataset(
            work)
        self.assertEqual(
            res['status'],
            SUCCESS)
        self.assertEqual(
            res['err'],
            None)
        self.assertTrue(
            res['rec'] is not None)
        self.assertEqual(
            res['rec']['initial_size'],
            3111)
        self.assertTrue(
            res['rec']['initial_data'] is not None)
        self.assertEqual(
            res['rec']['prepared_size'],
            3743)
        self.assertTrue(
            res['rec']['prepared_data'] is not None)
    # end of test_prepare_pricing_data_success

# end of TestPreparePricingDataset
