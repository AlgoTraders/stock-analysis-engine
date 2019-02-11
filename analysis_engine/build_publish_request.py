"""
Helper for building a dictionary for the:
``analysis_engine.publish.publish`` function
"""

import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_publish_request(
        ticker=None,
        tickers=None,
        convert_to_json=False,
        output_file=None,
        compress=False,
        redis_enabled=ae_consts.ENABLED_REDIS_PUBLISH,
        redis_key=None,
        redis_address=ae_consts.REDIS_ADDRESS,
        redis_db=ae_consts.REDIS_DB,
        redis_password=ae_consts.REDIS_PASSWORD,
        redis_expire=ae_consts.REDIS_EXPIRE,
        redis_serializer='json',
        redis_encoding='utf-8',
        s3_enabled=ae_consts.ENABLED_S3_UPLOAD,
        s3_key=None,
        s3_address=ae_consts.S3_ADDRESS,
        s3_bucket=ae_consts.S3_BUCKET,
        s3_access_key=ae_consts.S3_ACCESS_KEY,
        s3_secret_key=ae_consts.S3_SECRET_KEY,
        s3_region_name=ae_consts.S3_REGION_NAME,
        s3_secure=ae_consts.S3_SECURE,
        slack_enabled=False,
        slack_code_block=False,
        slack_full_width=False,
        verbose=False,
        label='publisher'):
    """build_publish_request

    Build a dictionary for helping to quickly publish
    to multiple optional endpoints:
    - a local file path (``output_file``)
    - minio (``s3_bucket`` and ``s3_key``)
    - redis (``redis_key``)
    - slack

    :param ticker: ticker
    :param tickers: optional - list of tickers
    :param label: optional - algo log tracking name
    :param output_file: path to save the data
        to a file
    :param compress: optional - compress before publishing
    :param verbose: optional - boolean to log output
    :param kwargs: optional - future argument support

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``ENABLED_REDIS_PUBLISH``)
    :param redis_key: string - key to save the data in redis
        (default is ``None``)
    :param redis_address: Redis connection string format: ``host:port``
        (default is ``REDIS_ADDRESS``)
    :param redis_db: Redis db to use
        (default is ``REDIS_DB``)
    :param redis_password: optional - Redis password
        (default is ``REDIS_PASSWORD``)
    :param redis_expire: optional - Redis expire value
        (default is ``REDIS_EXPIRE``)
    :param redis_serializer: not used yet - support for future
        pickle objects in redis (default is ``json``)
    :param redis_encoding: format of the encoded key in redis
        (default is ``utf-8``)

    **(Optional) Minio (S3) connectivity arguments**

    :param s3_enabled: bool - toggle for auto-archiving on Minio (S3)
        (default is ``ENABLED_S3_UPLOAD``)
    :param s3_key: string - key to save the data in redis
        (default is ``None``)
    :param s3_address: Minio S3 connection string format: ``host:port``
        (default is ``S3_ADDRESS``)
    :param s3_bucket: S3 Bucket for storing the artifacts
        (default is ``S3_BUCKET``) which should be viewable on a browser:
        http://localhost:9000/minio/dev/
    :param s3_access_key: S3 Access key
        (default is ``S3_ACCESS_KEY``)
    :param s3_secret_key: S3 Secret key
        (default is ``S3_SECRET_KEY``)
    :param s3_region_name: S3 region name
        (default is ``S3_REGION_NAME``)
    :param s3_secure: Transmit using tls encryption
        (default is ``S3_SECURE``)

    **(Optional) Slack arguments**

    :param slack_enabled: optional - boolean for
        publishing to slack
    :param slack_code_block: optional - boolean for
        publishing as a code black in slack
    :param slack_full_width: optional - boolean for
        publishing as a to slack using the full
        width allowed
    """
    use_tickers = []
    if ticker:
        use_tickers = [
            ticker.upper()
        ]
    if tickers:
        for t in tickers:
            if t not in use_tickers:
                use_tickers.append(t.upper())

    work = {
        'tickers': use_tickers,
        'label': label,
        'convert_to_json': convert_to_json,
        'output_file': output_file,
        'compress': compress,
        'redis_enabled': redis_enabled,
        'redis_key': redis_key,
        'redis_address': redis_address,
        'redis_db': redis_db,
        'redis_password': redis_password,
        'redis_expire': redis_expire,
        'redis_serializer': redis_serializer,
        'redis_encoding': redis_encoding,
        's3_enabled': s3_enabled,
        's3_key': s3_key,
        's3_address': s3_address,
        's3_bucket': s3_bucket,
        's3_access_key': s3_access_key,
        's3_secret_key': s3_secret_key,
        's3_region_name': s3_region_name,
        's3_secure': s3_secure,
        'slack_enabled': slack_enabled,
        'slack_code_block': slack_code_block,
        'slack_full_width': slack_full_width,
        'verbose': verbose,
        'version': 1,
        'label': label
    }

    log.debug(f'created publish_request={ae_consts.ppj(work)}')

    return work
# end of build_publish_request
