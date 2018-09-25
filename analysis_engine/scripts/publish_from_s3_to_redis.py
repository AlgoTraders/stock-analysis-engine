#!/usr/bin/env python

"""

Publish the contents of an S3 key to a
Redis key

Steps:
------

1) Parse arguments
2) Download pricing data as a Celery task
3) Publish pricing data as a Celery tasks
4) Coming Soon - Start buy/sell analysis as Celery task(s)

"""

import argparse
import analysis_engine.work_tasks.publish_from_s3_to_redis \
    as task_publisher
from celery import signals
from spylunking.log.setup_logging import build_colorized_logger
from celery_loaders.work_tasks.get_celery_app import get_celery_app
from analysis_engine.api_requests import build_publish_from_s3_to_redis_request
from analysis_engine.consts import LOG_CONFIG_PATH
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import WORKER_BROKER_URL
from analysis_engine.consts import WORKER_BACKEND_URL
from analysis_engine.consts import INCLUDE_TASKS
from analysis_engine.consts import SSL_OPTIONS
from analysis_engine.consts import TRANSPORT_OPTIONS
from analysis_engine.consts import S3_ACCESS_KEY
from analysis_engine.consts import S3_SECRET_KEY
from analysis_engine.consts import S3_REGION_NAME
from analysis_engine.consts import S3_ADDRESS
from analysis_engine.consts import S3_SECURE
from analysis_engine.consts import S3_BUCKET
from analysis_engine.consts import S3_KEY
from analysis_engine.consts import REDIS_ADDRESS
from analysis_engine.consts import REDIS_KEY
from analysis_engine.consts import REDIS_PASSWORD
from analysis_engine.consts import REDIS_DB
from analysis_engine.consts import REDIS_EXPIRE
from analysis_engine.consts import get_status
from analysis_engine.consts import ppj
from analysis_engine.consts import is_celery_disabled


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


log = build_colorized_logger(
    name='pub-from-s3-to-redis',
    log_config_path=LOG_CONFIG_PATH)


def publish_from_s3_to_redis():
    """publish_from_s3_to_redis

    Download an S3 key and publish it's contents to Redis

    """

    log.info(
        'start - {}'.format(
            __name__))

    parser = argparse.ArgumentParser(
        description=(
            'Download and store the latest stock pricing, '
            'news, and options chain data '
            'and store it in S3 and Redis. '
            'Once stored, this will also '
            'start the buy and sell trading analysis.'))
    parser.add_argument(
        '-t',
        help=(
            'ticker'),
        required=True,
        dest='ticker')
    parser.add_argument(
        '-i',
        help=(
            'optional - ticker id '
            'not used without a database'),
        required=False,
        dest='ticker_id')
    parser.add_argument(
        '-l',
        help=(
            'optional - path to the log config file'),
        required=False,
        dest='log_config_path')
    parser.add_argument(
        '-b',
        help=(
            'optional - broker url for Celery'),
        required=False,
        dest='broker_url')
    parser.add_argument(
        '-B',
        help=(
            'optional - backend url for Celery'),
        required=False,
        dest='backend_url')
    parser.add_argument(
        '-k',
        help=(
            'optional - s3 access key'),
        required=False,
        dest='s3_access_key')
    parser.add_argument(
        '-s',
        help=(
            'optional - s3 secret key'),
        required=False,
        dest='s3_secret_key')
    parser.add_argument(
        '-a',
        help=(
            'optional - s3 address format: <host:port>'),
        required=False,
        dest='s3_address')
    parser.add_argument(
        '-S',
        help=(
            'optional - s3 ssl or not'),
        required=False,
        dest='s3_secure')
    parser.add_argument(
        '-u',
        help=(
            'optional - s3 bucket name'),
        required=False,
        dest='s3_bucket_name')
    parser.add_argument(
        '-g',
        help=(
            'optional - s3 region name'),
        required=False,
        dest='s3_region_name')
    parser.add_argument(
        '-p',
        help=(
            'optional - redis_password'),
        required=False,
        dest='redis_password')
    parser.add_argument(
        '-r',
        help=(
            'optional - redis_address format: <host:port>'),
        required=False,
        dest='redis_address')
    parser.add_argument(
        '-n',
        help=(
            'optional - redis and s3 key name'),
        required=False,
        dest='keyname')
    parser.add_argument(
        '-m',
        help=(
            'optional - redis database number (4 by default)'),
        required=False,
        dest='redis_db')
    parser.add_argument(
        '-x',
        help=(
            'optional - redis expiration in seconds'),
        required=False,
        dest='redis_expire')
    parser.add_argument(
        '-d',
        help=(
            'debug'),
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    ticker = TICKER
    ticker_id = TICKER_ID
    ssl_options = SSL_OPTIONS
    transport_options = TRANSPORT_OPTIONS
    broker_url = WORKER_BROKER_URL
    backend_url = WORKER_BACKEND_URL
    include_tasks = INCLUDE_TASKS
    s3_access_key = S3_ACCESS_KEY
    s3_secret_key = S3_SECRET_KEY
    s3_region_name = S3_REGION_NAME
    s3_address = S3_ADDRESS
    s3_secure = S3_SECURE
    s3_bucket_name = S3_BUCKET
    s3_key = S3_KEY
    redis_address = REDIS_ADDRESS
    redis_key = REDIS_KEY
    redis_password = REDIS_PASSWORD
    redis_db = REDIS_DB
    redis_expire = REDIS_EXPIRE
    debug = False

    if args.ticker:
        ticker = args.ticker.upper()
    if args.ticker_id:
        ticker = args.ticker_id
    if args.broker_url:
        broker_url = args.broker_url
    if args.backend_url:
        backend_url = args.backend_url
    if args.s3_access_key:
        s3_access_key = args.s3_access_key
    if args.s3_secret_key:
        s3_secret_key = args.s3_secret_key
    if args.s3_region_name:
        s3_region_name = args.s3_region_name
    if args.s3_address:
        s3_address = args.s3_address
    if args.s3_secure:
        s3_secure = args.s3_secure
    if args.s3_bucket_name:
        s3_bucket_name = args.s3_bucket_name
    if args.keyname:
        s3_key = args.keyname
        redis_key = args.keyname
    if args.redis_address:
        redis_address = args.redis_address
    if args.redis_password:
        redis_password = args.redis_password
    if args.redis_db:
        redis_db = args.redis_db
    if args.redis_expire:
        redis_expire = args.redis_expire
    if args.debug:
        debug = True

    work = build_publish_from_s3_to_redis_request()

    work['ticker'] = ticker
    work['ticker_id'] = ticker_id
    work['s3_bucket'] = s3_bucket_name
    work['s3_key'] = s3_key
    work['redis_key'] = redis_key
    work['s3_access_key'] = s3_access_key
    work['s3_secret_key'] = s3_secret_key
    work['s3_region_name'] = s3_region_name
    work['s3_address'] = s3_address
    work['s3_secure'] = s3_secure
    work['redis_address'] = redis_address
    work['redis_password'] = redis_password
    work['redis_db'] = redis_db
    work['redis_expire'] = redis_expire
    work['debug'] = debug
    work['label'] = 'ticker={}'.format(
        ticker)

    path_to_tasks = 'analysis_engine.work_tasks'
    task_name = (
        '{}.publish_from_s3_to_redis.publish_from_s3_to_redis'.format(
            path_to_tasks))
    task_res = None
    if is_celery_disabled():
        work['celery_disabled'] = True
        log.debug(
            'starting without celery work={}'.format(
                ppj(work)))
        task_res = task_publisher.publish_from_s3_to_redis(
            work)
        log.info(
            'done - result={} '
            'task={} status={} '
            'err={} label={}'.format(
                ppj(task_res),
                task_name,
                get_status(status=task_res['status']),
                task_res['err'],
                work['label']))
    else:
        log.info(
            'connecting to broker={} backend={}'.format(
                broker_url,
                backend_url))

        # Get the Celery app
        app = get_celery_app(
            name=__name__,
            auth_url=broker_url,
            backend_url=backend_url,
            ssl_options=ssl_options,
            transport_options=transport_options,
            include_tasks=include_tasks)

        log.info(
            'calling task={} - work={}'.format(
                task_name,
                ppj(work)))
        job_id = app.send_task(
            task_name,
            (work,))
        log.info(
            'calling task={} - success job_id={}'.format(
                task_name,
                job_id))
    # end of if/else
# end of publish_from_s3_to_redis


if __name__ == '__main__':
    publish_from_s3_to_redis()
