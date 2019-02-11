"""
Dataset Publishing API
"""

import json
import boto3
import redis
import zlib
import analysis_engine.consts as ae_consts
import analysis_engine.compress_data as compress_data
import analysis_engine.set_data_in_redis_key as redis_utils
import analysis_engine.send_to_slack as slack_utils
import analysis_engine.write_to_file as file_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def publish(
        data,
        label=None,
        convert_to_json=False,
        is_df=False,
        output_file=None,
        df_compress=False,
        compress=False,
        redis_enabled=True,
        redis_key=None,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        redis_serializer='json',
        redis_encoding='utf-8',
        s3_enabled=True,
        s3_key=None,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=False,
        slack_enabled=False,
        slack_code_block=False,
        slack_full_width=False,
        verbose=False,
        silent=False,
        **kwargs):
    """publish

    Publish ``data`` to multiple optional endpoints:
    - a local file path (``output_file``)
    - minio (``s3_bucket`` and ``s3_key``)
    - redis (``redis_key``)
    - slack

    :return: status value
    :param data: data to publish
    :param convert_to_json: convert ``data`` to a
        json-serialized string. this function will throw if
        ``json.dumps(data)`` fails
    :param is_df: convert ``pd.DataFrame`` using
        ``pd.DataFrame.to_json()`` to a
        json-serialized string. this function will throw if
        ``to_json()`` fails
    :param label: log tracking label
    :param output_file: path to save the data
        to a file
    :param df_compress: optional - compress data that is a
        ``pandas.DataFrame`` before publishing
    :param compress: optional - compress before publishing
        (default is ``False``)
    :param verbose: optional - boolean to log output
        (default is ``False``)
    :param silent: optional - boolean no log output
        (default is ``False``)
    :param kwargs: optional - future argument support

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``True``)
    :param redis_key: string - key to save the data in redis
        (default is ``None``)
    :param redis_address: Redis connection string format: ``host:port``
        (default is ``localhost:6379``)
    :param redis_db: Redis db to use
        (default is ``0``)
    :param redis_password: optional - Redis password
        (default is ``None``)
    :param redis_expire: optional - Redis expire value
        (default is ``None``)
    :param redis_serializer: not used yet - support for future
        pickle objects in redis
    :param redis_encoding: format of the encoded key in redis

    **(Optional) Minio (S3) connectivity arguments**

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

    **(Optional) Slack arguments**

    :param slack_enabled: optional - boolean for
        publishing to slack
    :param slack_code_block: optional - boolean for
        publishing as a code black in slack
    :param slack_full_width: optional - boolean for
        publishing as a to slack using the full
        width allowed
    """

    status = ae_consts.NOT_RUN
    use_data = data
    if (
            not df_compress and
            not is_df and
            not use_data):
        log.info('missing data')
        return ae_consts.INVALID

    if convert_to_json and not is_df:
        if verbose:
            log.debug('start convert to json')
        use_data = json.dumps(data)
        if verbose:
            log.debug('done convert to json')
    if is_df:
        if verbose:
            log.debug('start df to_json')
        use_data = data.to_json(
            orient='records',
            date_format='iso')
        if verbose:
            log.debug('done df to_json')

    already_compressed = False
    if df_compress:
        use_data = compress_data.compress_data(
            data=data)
        already_compressed = True
    elif compress and not df_compress:
        if verbose:
            log.debug('compress start')
        use_data = zlib.compress(
            use_data.encode(
                redis_encoding), 9)
        already_compressed = True
        if verbose:
            log.debug('compress end')

    num_bytes = len(use_data)
    num_mb = ae_consts.get_mb(num_bytes)

    if verbose:
        log.debug(
            f'start - file={output_file} s3_key={s3_key} '
            f'redis_key={redis_key} slack={slack_enabled} '
            f'compress={compress} size={num_mb}MB')

    if s3_enabled and s3_address and s3_bucket and s3_key:
        endpoint_url = f'http{"s" if s3_secure else ""}://{s3_address}'

        if verbose:
            log.debug(
                f's3 start - {label} endpoint_url={endpoint_url} '
                f'region={s3_region_name}')

        s3 = boto3.resource(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            region_name=s3_region_name,
            config=boto3.session.Config(
                signature_version='s3v4')
        )

        if s3.Bucket(s3_bucket) not in s3.buckets.all():
            if verbose:
                log.debug(f's3 creating bucket={s3_bucket} {label}')
            s3.create_bucket(
                Bucket=s3_bucket)

        if verbose:
            log.debug(
                f's3 upload start - bytes={num_mb} to '
                f'{s3_bucket}:{s3_key} {label}')

        s3.Bucket(
            s3_bucket).put_object(
                Key=s3_key,
                Body=use_data)

        if verbose:
            log.debug(
                f's3 upload done - bytes={num_mb} to '
                f'{s3_bucket}:{s3_key} {label}')

    # end of s3_enabled

    if redis_enabled and redis_address and redis_key:
        redis_split = redis_address.split(':')
        redis_host = redis_split[0]
        redis_port = int(redis_split[1])
        log.debug(
            f'{label if label else ""} '
            f'redis={redis_host}:{redis_port}@{redis_db} connect '
            f'key={redis_key} expire={redis_expire}')

        rc = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db)

        redis_res = redis_utils.set_data_in_redis_key(
            label=label,
            client=rc,
            key=redis_key,
            data=use_data,
            already_compressed=already_compressed,
            serializer=redis_serializer,
            encoding=redis_encoding,
            expire=redis_expire,
            px=None,
            nx=False,
            xx=False)

        if redis_res['status'] != ae_consts.SUCCESS:
            log.error(
                f'redis failed - '
                f'{ae_consts.get_status(status=redis_res["status"])} '
                f'{redis_res["err"]}')
            return ae_consts.REDIS_FAILED
    # end of redis_enabled

    if output_file:
        if verbose:
            log.debug(f'file start - output_file={output_file}')
        file_exists = file_utils.write_to_file(
            output_file=output_file,
            data=data)
        if not file_exists:
            log.error(
                f'file failed - did not find '
                f'output_file={output_file}')
            return ae_consts.FILE_FAILED
        if verbose:
            log.debug(f'file done - output_file={output_file}')
    # end of writing to file

    if slack_enabled:
        if verbose:
            log.debug('slack start')
        slack_utils.post_success(
            msg=use_data,
            block=slack_code_block,
            full_width=slack_full_width)
        if verbose:
            log.debug('slack end')
    # end of sending to slack

    status = ae_consts.SUCCESS

    if verbose:
        log.debug(
            f'end - {ae_consts.get_status(status=status)} file={output_file} '
            f's3_key={s3_key} redis_key={redis_key} slack={slack_enabled} '
            f'compress={compress} size={num_mb}MB')

    return status
# end of publish
