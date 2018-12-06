"""
Load an ``Trading History`` dataset from file, s3 -
redis coming soon

Supported Datasets:

- ``SA_DATASET_TYPE_TRADING_HISTORY`` - trading history datasets

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import os
import analysis_engine.consts as consts
import analysis_engine.load_history_dataset_from_file as file_utils
import analysis_engine.load_history_dataset_from_s3 as s3_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_history_dataset(
        history_dataset=None,
        dataset_type=None,
        serialize_datasets=None,
        path_to_file=None,
        compress=None,
        encoding='utf-8',
        redis_enabled=None,
        redis_key=None,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        redis_serializer='json',
        redis_encoding='utf-8',
        s3_enabled=None,
        s3_key=None,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=None,
        slack_enabled=False,
        slack_code_block=False,
        slack_full_width=False,
        verbose=False):
    """load_history_dataset

    Load a ``Trading History`` Dataset from file, s3 - note
    redis is not supported yet

    :param history_dataset: optional - already loaded history dataset
    :param dataset_type: optional - dataset type
        (default is ``analysis_engine.consts.SA_DATASET_TYPE_TRADING_HISTORY``)
    :param path_to_file: optional - path to a trading history dataset
        in a file
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    :param compress: optional - boolean flag for decompressing
        the contents of the ``path_to_file`` if necessary
        (default is ``True`` and uses ``zlib`` for compression)
    :param encoding: optional - string for data encoding

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``analysis_engine.consts.ENABLED_REDIS_PUBLISH``)
    :param redis_key: string - key to save the data in redis
        (default is ``None``)
    :param redis_address: Redis connection string format: ``host:port``
        (default is ``analysis_engine.consts.REDIS_ADDRESS``)
    :param redis_db: Redis db to use
        (default is ``analysis_engine.consts.REDIS_DB``)
    :param redis_password: optional - Redis password
        (default is ``analysis_engine.consts.REDIS_PASSWORD``)
    :param redis_expire: optional - Redis expire value
        (default is ``None``)
    :param redis_serializer: not used yet - support for future
        pickle objects in redis
        (default is ``json``)
    :param redis_encoding: format of the encoded key in redis
        (default is ``utf-8``)

    **(Optional) Minio (S3) connectivity arguments**

    :param s3_enabled: bool - toggle for auto-archiving on Minio (S3)
        (default is ``analysis_engine.consts.ENABLED_S3_UPLOAD``)
    :param s3_key: string - key to save the data in redis
        (default is ``None``)
    :param s3_address: Minio S3 connection string format: ``host:port``
        (default is ``analysis_engine.consts.S3_ADDRESS``)
    :param s3_bucket: S3 Bucket for storing the artifacts
        (default is ``analysis_engine.consts.S3_BUCKET``) which should be
        viewable on a browser:
        http://localhost:9000/minio/
    :param s3_access_key: S3 Access key
        (default is ``analysis_engine.consts.S3_ACCESS_KEY``)
    :param s3_secret_key: S3 Secret key
        (default is ``analysis_engine.consts.S3_SECRET_KEY``)
    :param s3_region_name: S3 region name
        (default is ``analysis_engine.consts.S3_REGION_NAME``)
    :param s3_secure: Transmit using tls encryption
        (default is ``analysis_engine.consts.S3_SECURE``)

    **(Optional) Slack arguments**

    :param slack_enabled: optional - boolean for
        publishing to slack
    :param slack_code_block: optional - boolean for
        publishing as a code black in slack
    :param slack_full_width: optional - boolean for
        publishing as a to slack using the full
        width allowed

    Additonal arguments

    :param verbose: optional - bool for increasing
        logging
    """

    if not dataset_type:
        dataset_type = consts.SA_DATASET_TYPE_TRADING_HISTORY
    if not serialize_datasets:
        serialize_datasets = consts.DEFAULT_SERIALIZED_DATASETS
    if not redis_enabled:
        redis_enabled = consts.ENABLED_REDIS_PUBLISH
    if not redis_address:
        redis_address = consts.REDIS_ADDRESS
    if not redis_db:
        redis_db = consts.REDIS_DB
    if not redis_password:
        redis_password = consts.REDIS_PASSWORD
    if not s3_enabled:
        s3_enabled = consts.ENABLED_S3_UPLOAD
    if not s3_address:
        s3_address = consts.S3_ADDRESS
    if not s3_bucket:
        s3_bucket = consts.S3_BUCKET
    if not s3_access_key:
        s3_access_key = consts.S3_ACCESS_KEY
    if not s3_secret_key:
        s3_secret_key = consts.S3_SECRET_KEY
    if not s3_region_name:
        s3_region_name = consts.S3_REGION_NAME
    if not s3_secure:
        s3_secure = consts.S3_SECURE
    if compress is None:
        compress = consts.ALGO_HISTORY_COMPRESS

    use_ds = history_dataset
    if not use_ds:
        log.info(
            'loading {} from file={} s3={} redis={}'.format(
                consts.get_status(status=dataset_type),
                path_to_file,
                s3_key,
                redis_key))
    # load if not created

    supported_type = False
    if dataset_type == consts.SA_DATASET_TYPE_TRADING_HISTORY:
        supported_type = True
        if (path_to_file and
                not use_ds):
            if not os.path.exists(path_to_file):
                log.error('missing file: {}'.format(path_to_file))
            use_ds = file_utils.load_history_dataset_from_file(
                path_to_file=path_to_file,
                compress=compress,
                encoding=redis_encoding,
                serialize_datasets=serialize_datasets)
        elif (s3_key and
                not use_ds):
            use_ds = s3_utils.load_history_dataset_from_s3(
                s3_key=s3_key,
                s3_address=s3_address,
                s3_bucket=s3_bucket,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_region_name=s3_region_name,
                s3_secure=s3_secure,
                compress=compress,
                encoding=redis_encoding,
                serialize_datasets=serialize_datasets)
    else:
        supported_type = False
        use_ds = None
        log.error(
            'loading {} from file={} s3={} redis={}'.format(
                dataset_type,
                path_to_file,
                s3_key,
                redis_key))
    # load if not created

    if not use_ds and supported_type:
        log.error(
            'unable to load a dataset from file={} '
            's3={} redis={}'.format(
                path_to_file,
                s3_key,
                redis_key))

    return use_ds
# end of load_history_dataset
