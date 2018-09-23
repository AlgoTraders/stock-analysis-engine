"""
Publish Pricing from an S3 Key to Redis

- redis - using `redis-py <https://github.com/andymccurdy/redis-py>`__
- s3 - using boto3
"""

import boto3
import redis
import analysis_engine.build_result as build_result
import analysis_engine.get_task_results
import analysis_engine.work_tasks.custom_task
import analysis_engine.options_dates
import analysis_engine.get_pricing
import analysis_engine.set_data_in_redis_key as redis_set
from celery.task import task
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import get_status
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
from analysis_engine.consts import ppj
from analysis_engine.consts import to_f
import analysis_engine.s3_read_contents_from_key as \
    s3_read_contents_from_key

log = build_colorized_logger(
    name=__name__)


@task(
    bind=True,
    base=analysis_engine.work_tasks.custom_task.CustomTask,
    queue='publish_from_s3_to_redis')
def publish_from_s3_to_redis(
        self,
        work_dict):
    """publish_from_s3_to_redis

    Publish Ticker Data from S3 to Redis

    :param work_dict: dictionary for key/values
    """

    label = 'pub-s3-to-redis'

    log.info((
        'task - {} - start '
        'work_dict={}').format(
            label,
            work_dict))

    ticker = TICKER
    ticker_id = TICKER_ID
    rec = {
        'ticker': None,
        'ticker_id': None,
        's3_enabled': True,
        'redis_enabled': True,
        's3_bucket': None,
        's3_key': None,
        'redis_key': None,
        'updated': None
    }
    res = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:
        ticker = work_dict.get(
            'ticker',
            TICKER)
        ticker_id = int(work_dict.get(
            'ticker_id',
            TICKER_ID))

        if not ticker:
            res = build_result.build_result(
                status=ERR,
                err='missing ticker',
                rec=rec)
            return res

        s3_key = work_dict.get(
            's3_key',
            None)
        s3_bucket_name = work_dict.get(
            's3_bucket',
            'pricing')
        redis_key = work_dict.get(
            'redis_key',
            None)
        updated = work_dict.get(
            'updated',
            None)
        serializer = work_dict.get(
            'serializer',
            'json')
        encoding = work_dict.get(
            'encoding',
            'utf-8')
        label = work_dict.get(
            'label',
            label)

        enable_s3_read = True
        enable_redis_publish = True

        rec['ticker'] = ticker
        rec['ticker_id'] = ticker_id
        rec['s3_bucket'] = s3_bucket_name
        rec['s3_key'] = s3_key
        rec['redis_key'] = redis_key
        rec['updated'] = updated
        rec['s3_enabled'] = enable_s3_read
        rec['redis_enabled'] = enable_redis_publish

        data = None

        if enable_s3_read:

            log.info(
                '{} parsing s3 values'.format(
                    label))
            access_key = work_dict.get(
                's3_access_key',
                S3_ACCESS_KEY)
            secret_key = work_dict.get(
                's3_secret_key',
                S3_SECRET_KEY)
            region_name = work_dict.get(
                's3_region_name',
                S3_REGION_NAME)
            service_address = work_dict.get(
                's3_address',
                S3_ADDRESS)
            secure = work_dict.get(
                's3_secure',
                S3_SECURE) == '1'

            endpoint_url = 'http://{}'.format(
                service_address)
            if secure:
                endpoint_url = 'https://{}'.format(
                    service_address)

            log.info((
                '{} building s3 endpoint_url={} '
                'region={}').format(
                    label,
                    endpoint_url,
                    region_name))

            s3 = boto3.resource(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region_name,
                config=boto3.session.Config(
                    signature_version='s3v4')
            )

            try:
                log.info((
                    '{} checking bucket={} exists').format(
                        label,
                        s3_bucket_name))
                if s3.Bucket(s3_bucket_name) not in s3.buckets.all():
                    log.info((
                        '{} creating bucket={}').format(
                            label,
                            s3_bucket_name))
                    s3.create_bucket(
                        Bucket=s3_bucket_name)
            except Exception as e:
                log.info((
                    '{} failed creating bucket={} '
                    'with ex={}').format(
                        label,
                        s3_bucket_name,
                        e))
            # end of try/ex for creating bucket

            try:
                log.info((
                    '{} reading to s3={}/{} '
                    'updated={}').format(
                        label,
                        s3_bucket_name,
                        s3_key,
                        updated))
                data = s3_read_contents_from_key.s3_read_contents_from_key(
                    s3=s3,
                    s3_bucket_name=s3_bucket_name,
                    s3_key=s3_key,
                    encoding=encoding,
                    convert_as_json=True)

                initial_size_value = \
                    len(str(data)) / 1024000
                initial_size_str = to_f(initial_size_value)
                if ev('DEBUG_S3', '0') == '1':
                    log.info(
                        '{} read s3={}/{} data={}'.format(
                            label,
                            s3_bucket_name,
                            s3_key,
                            ppj(data)))
                else:
                    log.info(
                        '{} read s3={}/{} data size={} MB'.format(
                            label,
                            s3_bucket_name,
                            s3_key,
                            initial_size_str))
            except Exception as e:
                err = (
                    '{} failed reading bucket={} '
                    'key={} ex={}').format(
                        label,
                        s3_bucket_name,
                        s3_key,
                        e)
                log.error(
                    err)
                res = build_result.build_result(
                    status=NOT_RUN,
                    err=err,
                    rec=rec)
            # end of try/ex for creating bucket
        else:
            log.info((
                '{} SKIP S3 read bucket={} '
                'key={}').format(
                    label,
                    s3_bucket_name,
                    s3_key))
        # end of if enable_s3_read

        if enable_redis_publish:
            redis_address = work_dict.get(
                'redis_address',
                REDIS_ADDRESS)
            redis_key = work_dict.get(
                'redis_key',
                REDIS_KEY)
            redis_password = work_dict.get(
                'redis_password',
                REDIS_PASSWORD)
            redis_db = work_dict.get(
                'redis_db',
                None)
            if not redis_db:
                redis_db = REDIS_DB
            redis_expire = None
            if 'redis_expire' in work_dict:
                redis_expire = work_dict.get(
                    'redis_expire',
                    REDIS_EXPIRE)
            log.info(
                'redis enabled address={}@{} '
                'key={}'.format(
                    redis_address,
                    redis_db,
                    redis_key))
            redis_host = redis_address.split(':')[0]
            redis_port = redis_address.split(':')[1]
            try:
                if ev('DEBUG_REDIS', '0') == '1':
                    log.info((
                        '{} publishing redis={}:{} '
                        'db={} key={} '
                        'updated={} expire={} '
                        'data={}').format(
                            label,
                            redis_host,
                            redis_port,
                            redis_db,
                            redis_key,
                            updated,
                            redis_expire,
                            ppj(data)))
                else:
                    log.info((
                        '{} publishing redis={}:{} '
                        'db={} key={} '
                        'updated={} expire={}').format(
                            label,
                            redis_host,
                            redis_port,
                            redis_db,
                            redis_key,
                            updated,
                            redis_expire))
                # end of if/else

                rc = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db)

                redis_set_res = redis_set.set_data_in_redis_key(
                    label=label,
                    client=rc,
                    key=redis_key,
                    data=data,
                    serializer=serializer,
                    encoding=encoding,
                    expire=redis_expire,
                    px=None,
                    nx=False,
                    xx=False)

                log.info(
                    '{} redis_set status={} err={}'.format(
                        label,
                        get_status(redis_set_res['status']),
                        redis_set_res['err']))

            except Exception as e:
                log.error((
                    '{} failed - redis publish to '
                    'key={} ex={}').format(
                        label,
                        redis_key,
                        e))
            # end of try/ex for creating bucket
        else:
            log.info((
                '{} SKIP REDIS publish '
                'key={}').format(
                    label,
                    redis_key))
        # end of if enable_redis_publish

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - publish_from_s3_to_redis '
                'dict={} with ex={}').format(
                    work_dict,
                    e))
        log.error((
            '{} - {}').format(
                label,
                res['err']))
    # end of try/ex

    log.info((
        'task - {} - done - status={}').format(
            label,
            get_status(res['status'])))

    return res
# end of publish_from_s3_to_redis


def run_publish_from_s3_to_redis(
        work_dict):
    """run_publish_from_s3_to_redis

    Celery wrapper for running without celery

    :param work_dict: task data
    """
    log.info((
        'run_publish_from_s3_to_redis start - req={}').format(
            work_dict))

    rec = {}
    response = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)
    task_res = {}

    # by default celery is not used for this one:
    if ev('CELERY_DISABLED', '1') == '1':
        task_res = publish_from_s3_to_redis(
            work_dict)  # note - this is not a named kwarg
    else:
        task_res = publish_from_s3_to_redis.delay(
            work_dict=work_dict)
    # if celery enabled

    response = build_result.build_result(
        status=task_res.get(
            'status',
            SUCCESS),
        err=task_res.get(
            'err',
            None),
        rec=task_res.get(
            'rec',
            rec))

    response_status = response['status']

    log.info((
        'run_publish_from_s3_to_redis done - '
        'status={} err={} rec={}').format(
            response_status,
            response['err'],
            response['rec']))

    return response
# end of run_publish_from_s3_to_redis
