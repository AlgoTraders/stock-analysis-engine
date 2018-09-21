"""
Prepare Pricing Dataset

- if key not in redis, load the key by the same name from s3
- prepare dataset from redis key
- the dataset will be stored as a dictionary with a pandas dataframe
"""

import datetime
import redis
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.get_data_from_redis_key as redis_get
import analysis_engine.get_task_results
import analysis_engine.work_tasks.custom_task
import analysis_engine.options_dates
import analysis_engine.get_pricing
import analysis_engine.work_tasks.publish_from_s3_to_redis as \
    s3_to_redis
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
from analysis_engine.consts import CELERY_DISABLED


log = build_colorized_logger(
    name=__name__)


@task(
    bind=True,
    base=analysis_engine.work_tasks.custom_task.CustomTask,
    queue='prepare_pricing_dataset')
def prepare_pricing_dataset(
        self,
        work_dict):
    """prepare_pricing_dataset

    Prepare dataset for analysis. Supports loading dataset from
    s3 if not found in redis. Outputs prepared artifact as a csv
    to s3 and redis.

    :param work_dict: dictionary for key/values
    """

    label = 'prepare'

    log.info(
        'task - {} - start '
        'work_dict={}'.format(
            label,
            work_dict))

    initial_data = None
    # prepared_data = None
    # df = None

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
        'prepared_s3_key': None,
        'prepared_s3_bucket': None,
        'prepared_redis_key': None,
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

        label = 'prepare ticker={}'.format(
            ticker)

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
        s3_access_key = work_dict.get(
            's3_access_key',
            S3_ACCESS_KEY)
        s3_secret_key = work_dict.get(
            's3_secret_key',
            S3_SECRET_KEY)
        s3_region_name = work_dict.get(
            's3_region_name',
            S3_REGION_NAME)
        s3_address = work_dict.get(
            's3_address',
            S3_ADDRESS)
        s3_secure = work_dict.get(
            's3_secure',
            S3_SECURE) == '1'
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
        updated = work_dict.get(
            'updated',
            datetime.datetime.utcnow().strftime(
                '%Y_%m_%d_%H_%M_%S'))
        prepared_s3_key = work_dict.get(
            'prepared_s3_key',
            '{}_{}.csv'.format(
                ticker,
                updated))
        prepared_s3_bucket = work_dict.get(
            'prepared_s3_bucket',
            'prepared')
        prepared_redis_key = work_dict.get(
            'prepared_redis_key',
            'prepared')
        log.info(
            'redis enabled address={}@{} '
            'key={} prepare_s3={}:{} prepare_redis={}'.format(
                redis_address,
                redis_db,
                redis_key,
                prepared_s3_bucket,
                prepared_s3_key,
                prepared_redis_key))
        redis_host = redis_address.split(':')[0]
        redis_port = redis_address.split(':')[1]

        enable_s3 = True
        enable_redis_publish = True

        label += ''

        rec['ticker'] = ticker
        rec['ticker_id'] = ticker_id
        rec['s3_bucket'] = s3_bucket_name
        rec['s3_key'] = s3_key
        rec['redis_key'] = redis_key
        rec['prepared_s3_key'] = prepared_s3_key
        rec['prepared_s3_bucket'] = prepared_s3_bucket
        rec['prepared_redis_key'] = prepared_redis_key
        rec['updated'] = updated
        rec['s3_enabled'] = enable_s3
        rec['redis_enabled'] = enable_redis_publish

        try:
            log.info(
                '{} connecting redis={}:{} '
                'db={} key={} '
                'updated={} expire={}'.format(
                    label,
                    redis_host,
                    redis_port,
                    redis_db,
                    redis_key,
                    updated,
                    redis_expire))
            rc = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db)
        except Exception as e:
            err = (
                '{} failed - redis connection to address={}@{} '
                'key={} ex={}'.format(
                    label,
                    redis_address,
                    redis_key,
                    redis_db,
                    e))
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)
            return res
        # end of try/ex for connecting to redis

        initial_data = redis_get.get_data_from_redis_key(
            label=label,
            redis_client=rc)

        if enable_s3 and not initial_data:

            log.info(
                'failed to find redis_key={} trying s3'
                'from s3_key={} s3_bucket={} s3_address={}'.format(
                    redis_key,
                    s3_key,
                    s3_bucket_name,
                    s3_address))

            get_from_s3_req = \
                api_requests.build_publish_from_s3_to_redis_request()

            get_from_s3_req['s3_enabled'] = enable_s3
            get_from_s3_req['s3_access_key'] = s3_access_key
            get_from_s3_req['s3_secret_key'] = s3_secret_key
            get_from_s3_req['s3_region_name'] = s3_region_name
            get_from_s3_req['s3_address'] = s3_address
            get_from_s3_req['s3_secure'] = s3_secure
            get_from_s3_req['s3_key'] = s3_key
            get_from_s3_req['s3_bucket'] = s3_bucket_name
            get_from_s3_req['redis_key'] = redis_key

            log.info(
                '{} load from s3={} to '
                'redis={}'.format(
                    label,
                    s3_key,
                    redis_key))

            try:
                task_res = s3_to_redis.publish_from_s3_to_redis(
                    work_dict)  # note - this is not a named kwarg
                if task_res.get('status', ERR) == SUCCESS:
                    log.info(
                        '{} loaded s3={}:{} '
                        'to redis={}'.format(
                            label,
                            s3_bucket_name,
                            s3_key,
                            redis_key))
                else:
                    err = (
                        '{} ERR failed loading from bucket={} '
                        's3_key={} to redis_key={} with res={}'.format(
                            label,
                            s3_bucket_name,
                            s3_key,
                            redis_key,
                            task_res))
                    log.err(err)
                    res = build_result.build_result(
                        status=ERR,
                        err=err,
                        rec=rec)
                    return res
            except Exception as e:
                err = (
                    '{} EX failed loading bucket={} '
                    's3_key={} redis_key={} with ex={}'.format(
                        label,
                        s3_bucket_name,
                        s3_key,
                        redis_key,
                        e))
                log.error(err)
                res = build_result.build_result(
                    status=ERR,
                    err=err,
                    rec=rec)
                return res
            # end of try/ex for publishing from s3->redis
        # end of if enable_s3

        if not initial_data:
            err = (
                '{} did not find redis_key={} or '
                's3_key={} in bucket={}'.format(
                    label,
                    redis_key,
                    s3_key,
                    s3_bucket_name))
            log.error(err)
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)
            return res
        else:
            log.info(
                'got data: {}'.format(
                    str(initial_data)))
        # end of trying to get initial_data

        rc = None

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - prepare_pricing_dataset '
                'dict={} with ex={}'.format(
                    work_dict,
                    e)))
        log.error(
            '{} - {}'.format(
                label,
                res['err']))
    # end of try/ex

    log.info(
        'task - {} - done - status={}'.format(
            label,
            get_status(res['status'])))

    return res
# end of prepare_pricing_dataset


def run_prepare_pricing_dataset(
        work_dict):
    """run_prepare_pricing_dataset

    Celery wrapper for running without celery

    :param work_dict: task data
    """
    log.info(
        'run_prepare_pricing_dataset start - req={}'.format(
            work_dict))

    rec = {}
    response = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)
    task_res = {}

    # by default celery is not used for this one:
    if CELERY_DISABLED:
        task_res = prepare_pricing_dataset(
            work_dict)  # note - this is not a named kwarg
    else:
        task_res = prepare_pricing_dataset.delay(
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

    log.info(
        'run_prepare_pricing_dataset done - '
        'status={} err={} rec={}'.format(
            response_status,
            response['err'],
            response['rec']))

    return response
# end of run_prepare_pricing_dataset
