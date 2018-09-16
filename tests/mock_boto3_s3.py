"""
Mock boto3 s3 objects
"""

from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


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

        log.info(
            'mock - MockBotoS3Bucket.put_object(Key={}, '
            'Body={})'.format(
                Key,
                Body))

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
                'adding bucket={} total={}'.format(
                    bucket_name,
                    len(self.buckets) + 1))
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
            'MockBotoS3.Bucket({})'.format(
                name))
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
            'mock - MockBotoS3.create_bucket(Bucket={})'.format(
                Bucket))
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
