#!/usr/bin/env python

"""

Stock Analysis Command Line Tool

Supports
--------

- Preparing a dataset from s3 or redis. A prepared
  dataset can be used for analysis.
- Coming Soon - Analyze datasets and store output (generated csvs)
  in s3 and redis.
- Coming Soon - Make predictions using an analyzed dataset

.. note:: if the output redis key or s3 key already exists, this
          process will overwrite the previously stored values
"""

import sys
import argparse
import analysis_engine.work_tasks.prepare_pricing_dataset \
    as prepare_pricing_dataset
from celery import signals
from spylunking.log.setup_logging import build_colorized_logger
from celery_loaders.work_tasks.get_celery_app import get_celery_app
from analysis_engine.api_requests import build_prepare_dataset_request
from analysis_engine.consts import SA_MODE_PREPARE
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
    name='sa',
    log_config_path=LOG_CONFIG_PATH)


def run_sa_tool():
    """sa_tool

    Run buy and sell analysis on a stock to send alerts to subscribed
    users

    """

    log.debug('start - sa')

    parser = argparse.ArgumentParser(
        description=(
            'stock analysis tool'))
    parser.add_argument(
        '-t',
        help=(
            'ticker'),
        required=True,
        dest='ticker')
    parser.add_argument(
        '-f',
        help=(
            'run in mode: prepare dataset from '
            'redis key or s3 key'),
        required=False,
        dest='prepare_mode',
        action='store_true')
    parser.add_argument(
        '-o',
        help=(
            'output s3 and redis key'),
        dest='output_key')
    parser.add_argument(
        '-j',
        help=(
            'output s3 bucket - default bucket is named '
            'prepared'),
        required=False,
        dest='output_s3_bucket')
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
        '-z',
        help=(
            'optional - strike price'),
        required=False,
        dest='strike')
    parser.add_argument(
        '-c',
        help=(
            'optional - contract type "C" for calls "P" for puts'),
        required=False,
        dest='contract_type')
    parser.add_argument(
        '-P',
        help=(
            'optional - get pricing data if "1" or "0" disabled'),
        required=False,
        dest='get_pricing')
    parser.add_argument(
        '-N',
        help=(
            'optional - get news data if "1" or "0" disabled'),
        required=False,
        dest='get_news')
    parser.add_argument(
        '-O',
        help=(
            'optional - get options data if "1" or "0" disabled'),
        required=False,
        dest='get_options')
    parser.add_argument(
        '-U',
        help=(
            'optional - s3 enabled for publishing if "1" or '
            '"0" is disabled'),
        required=False,
        dest='s3_enabled')
    parser.add_argument(
        '-R',
        help=(
            'optional - redis enabled for publishing if "1" or '
            '"0" is disabled'),
        required=False,
        dest='redis_enabled')
    parser.add_argument(
        '-i',
        help=(
            'optional - ignore column names (comma separated)'),
        required=False,
        dest='ignore_columns')
    parser.add_argument(
        '-d',
        help=(
            'debug'),
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    mode = 'prepare'
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
    output_s3_key = None
    output_redis_key = None
    output_s3_bucket = None
    s3_enabled = True
    redis_enabled = True
    ignore_columns = None
    debug = False

    if args.ticker:
        ticker = args.ticker.upper()
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
    if args.s3_enabled:
        s3_enabled = args.s3_enabled == '1'
    if args.redis_enabled:
        redis_enabled = args.redis_enabled == '1'
    if args.prepare_mode:
        mode = SA_MODE_PREPARE
    if args.output_key:
        output_s3_key = args.output_key
        output_redis_key = args.output_key
    if args.output_s3_bucket:
        output_s3_bucket = args.output_s3_bucket
    if args.ignore_columns:
        ignore_columns_org = args.ignore_columns
        ignore_columns = ignore_columns_org.split(",")

    if args.debug:
        debug = True

    work = None
    task_name = None
    path_to_tasks = 'analysis_engine.work_tasks'
    if mode == SA_MODE_PREPARE:
        task_name = (
            '{}.'
            'prepare_pricing_dataset.prepare_pricing_dataset').format(
                path_to_tasks)
        work = build_prepare_dataset_request()
        if output_s3_key:
            work['prepared_s3_key'] = output_s3_key
        if output_s3_bucket:
            work['prepared_s3_bucket'] = output_s3_bucket
        if output_redis_key:
            work['prepared_redis_key'] = output_redis_key
        work['ignore_columns'] = ignore_columns
    # end of handling mode-specific arg assignments

    # sanity checking the work and task are valid
    if not work:
        log.error(
            'usage error: missing a supported mode: '
            '-f (for prepare a dataset) ')
        sys.exit(1)
    if not task_name:
        log.error(
            'usage error: missing a supported task_name')
        sys.exit(1)
    # end of sanity checks

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
    work['s3_enabled'] = s3_enabled
    work['redis_enabled'] = redis_enabled
    work['debug'] = debug
    work['label'] = 'ticker={}'.format(
        ticker)

    task_res = None
    if is_celery_disabled():
        work['celery_disabled'] = True
        log.debug(
            'starting without celery work={}'.format(
                ppj(work)))
        if mode == SA_MODE_PREPARE:
            task_res = prepare_pricing_dataset.prepare_pricing_dataset(
                work)
        log.info(
            'done - mode={} result={}'.format(
                get_status(status=mode),
                ppj(task_res)))
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
        log.info((
            'calling task={} - success job_id={}').format(
                task_name,
                job_id))
    # end of if/else

# end of run_sa_tool


if __name__ == '__main__':
    run_sa_tool()
