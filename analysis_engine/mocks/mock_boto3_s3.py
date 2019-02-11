"""
Mock boto3 s3 objects
"""

import os
import json
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def mock_s3_read_contents_from_key_ev(
        s3,
        s3_bucket_name,
        s3_key,
        encoding,
        convert_as_json):
    """mock_s3_read_contents_from_key

    :param s3: s3 client
    :param s3_bucket_name: bucket name
    :param s3_key: key
    :param encoding: utf-8
    :param convert_as_json: convert to json
    """

    env_key = 'TEST_S3_CONTENTS'
    str_contents = ae_consts.ev(
        env_key,
        None)

    log.info(
        f'returning mock s3={s3_bucket_name}:{s3_key} contents={str_contents} '
        f'encoding={encoding} json={convert_as_json} env_key={env_key}')

    if not str_contents:
        return str_contents

    if convert_as_json:
        return json.loads(str_contents)
# end of mock_s3_read_contents_from_key_ev


def mock_publish_from_s3_to_redis(
        work_dict):
    """mock_publish_from_s3_to_redis

    :param work_dict: dictionary for driving the task
    """

    env_key = 'TEST_S3_CONTENTS'
    redis_key = work_dict.get(
        'redis_key',
        env_key)
    str_dict = ae_consts.ev(
        env_key,
        None)
    log.info(
        'mock_publish_from_s3_to_redis - '
        f'setting key={redis_key} value={str_dict}')
    data = None
    if str_dict:
        os.environ[redis_key] = str_dict
        data = str_dict.encode('utf-8')
    else:
        os.environ[redis_key] = ''
        data = None

    status = ae_consts.SUCCESS
    err = None
    return {
        'status': status,
        'err': err,
        'rec': {
            'data': data
        }
    }
# end of mock_publish_from_s3_to_redis


def mock_publish_from_s3_to_redis_err(
        work_dict):
    """mock_publish_from_s3_to_redis_err

    :param work_dict: dictionary for driving the task
    """

    env_key = 'TEST_S3_CONTENTS'
    redis_key = work_dict.get(
        'redis_key',
        env_key)
    str_dict = ae_consts.ev(
        env_key,
        None)
    log.info(
        'mock_publish_from_s3_to_redis_err - '
        f'setting key={redis_key} value={str_dict}')
    data = None
    if str_dict:
        os.environ[redis_key] = str_dict
        data = str_dict.encode('utf-8')
    else:
        os.environ[redis_key] = ''
        data = None

    status = ae_consts.ERR
    err = None
    return {
        'status': status,
        'err': err,
        'rec': {
            'data': data
        }
    }
# end of mock_publish_from_s3_to_redis_err


def mock_publish_from_s3_exception(
        work_dict):
    """mock_publish_from_s3_exception

    :param work_dict: dictionary for driving the task
    """
    raise Exception(
        'test mock_publish_from_s3_exception')
# end of mock_publish_from_s3_exception


class MockBotoS3Bucket:
    """MockBotoS3Bucket"""

    def __init__(
            self,
            name):
        """__init__

        build mock bucket

        :param name: name of the bucket
        """
        self.name = name
        self.datas = []  # payloads uploaded to s3
        self.keys = []   # keys uploaded to s3
    # end of __init__

    def put_object(
            self,
            Key=None,
            Body=None):
        """put_object

        :param Key: new Key name
        :param Body: new Payload in Key
        """

        log.debug(
            f'mock - MockBotoS3Bucket.put_object(Key={Key}, '
            f'Body={Body})')

        self.keys.append(Key)
        self.datas.append(Body)
    # end of put_object

# end of MockBotoS3Bucket


class MockBotoS3AllBuckets:
    """MockBotoS3AllBuckets"""

    def __init__(
            self):
        """__init__"""
        self.buckets = {}
    # end of __init__

    def add(
            self,
            bucket_name):
        """add

        :param bucket_name: bucket name to add
        """
        if bucket_name not in self.buckets:
            log.info(
                f'adding bucket={bucket_name} total={len(self.buckets) + 1}')
            self.buckets[bucket_name] = MockBotoS3Bucket(
                name=bucket_name)

        return self.buckets[bucket_name]
    # end of add

    def all(
            self):
        """all"""
        return self.buckets
    # end of all

# end of MockBotoS3AllBuckets


class MockBotoS3:
    """MockBotoS3"""

    def __init__(
            self,
            name='mock_s3',
            endpoint_url=None,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            region_name=None,
            config=None):
        """__init__

        build mock object

        :param name: name of client
        :param endpoint_url: endpoint url
        :param aws_access_key_id: aws access key
        :param aws_secret_access_key: aws secret key
        :param region_name: region name
        :param config: config object
        """

        self.name = name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.config = config
        self.buckets = MockBotoS3AllBuckets()
        self.keys = []
    # end of __init__

    def Bucket(
            self,
            name):
        """Bucket

        :param name: name of new bucket
        """
        log.info(
            f'MockBotoS3.Bucket({name})')
        return self.buckets.add(
            bucket_name=name)
    # end of Bucket

    def create_bucket(
            self,
            Bucket=None):
        """create_bucket

        :param bucket_name: name of the new bucket
        """
        log.info(
            f'mock - MockBotoS3.create_bucket(Bucket={Bucket})')
        return self.buckets.add(
            bucket_name=Bucket)
    # end of create_bucket

# end of MockBotoS3


def build_boto3_resource(
        name='mock_s3',
        endpoint_url=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        region_name=None,
        config=None):
    """build_boto3_resource

    :param name: name of client
    :param endpoint_url: endpoint url
    :param aws_access_key_id: aws access key
    :param aws_secret_access_key: aws secret key
    :param region_name: region name
    :param config: config object
    """

    if 's3' in name.lower():
        return MockBotoS3(
            name='mock_s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            config=config)
    else:
        return MockBotoS3(
            name='mock_s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            config=config)
# end of build_boto3_resource
