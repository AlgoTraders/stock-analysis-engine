"""
Helper for loading ``Trading History`` datasets from s3

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import boto3
import analysis_engine.consts as consts
import analysis_engine.prepare_history_dataset as prepare_utils
import analysis_engine.s3_read_contents_from_key as s3_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_history_dataset_from_s3(
        s3_key,
        s3_address,
        s3_bucket,
        s3_access_key,
        s3_secret_key,
        s3_region_name,
        s3_secure,
        serialize_datasets=consts.DEFAULT_SERIALIZED_DATASETS,
        convert_as_json=True,
        compress=False,
        encoding='utf-8'):
    """load_history_dataset_from_s3

    Load an algorithm-ready dataset for algorithm backtesting
    from a local file

    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    :param convert_as_json: optional - boolean flag for decoding
        as a dictionary
    :param compress: optional - boolean flag for decompressing
        the contents of the ``path_to_file`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding

    **Minio (S3) connectivity arguments**

    :param s3_enabled: bool - toggle for auto-archiving on Minio (S3)
        (default is ``True``)
    :param s3_key: string - key to save the data in redis
        (default is ``None``)
    :param s3_address: Minio S3 connection string format: ``host:port``
        (default is ``localhost:9000``)
    :param s3_bucket: S3 Bucket for storing the artifacts
        (default is ``dev``) which should be viewable on a browser:
        http://localhost:9000/minio/dev/
    :param s3_access_key: S3 Access key
        (default is ``trexaccesskey``)
    :param s3_secret_key: S3 Secret key
        (default is ``trex123321``)
    :param s3_region_name: S3 region name
        (default is ``us-east-1``)
    :param s3_secure: Transmit using tls encryption
        (default is ``False``)
    """
    log.info(
        'start s3={}:{}/{}'.format(
            s3_address,
            s3_bucket,
            s3_key))

    data_from_file = None

    endpoint_url = 'http://{}'.format(
        s3_address)
    if s3_secure:
        endpoint_url = 'https://{}'.format(
            s3_address)

    s3 = boto3.resource(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        region_name=s3_region_name,
        config=boto3.session.Config(signature_version='s3v4'))

    try:
        data_from_file = s3_utils.s3_read_contents_from_key(
            s3=s3,
            s3_bucket_name=s3_bucket,
            s3_key=s3_key,
            encoding=encoding,
            convert_as_json=convert_as_json,
            compress=compress)
    except Exception as e:
        if (
                'An error occurred (NoSuchBucket) '
                'when calling the GetObject operation') in str(e):
            msg = (
                'missing s3_bucket={} in s3_address={}'.format(
                    s3_address,
                    s3_bucket))
            log.error(msg)
            raise Exception(msg)
        else:
            raise Exception(e)

    if not data_from_file:
        log.error('missing data from s3={}:{}/{}'.format(
            s3_address,
            s3_bucket,
            s3_key))
        return None

    return prepare_utils.prepare_history_dataset(
        data=data_from_file,
        compress=False,
        convert_to_dict=False,
        encoding=encoding)
# end of load_history_dataset_from_s3
