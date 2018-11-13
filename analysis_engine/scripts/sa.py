#!/usr/bin/env python

"""

**Stock Analysis Command Line Tool**

1) Get an algorithm-ready dataset

- Fetch and extract algorithm-ready datasets
- Optional - Preparing a dataset from s3 or redis. A prepared
  dataset can be used for analysis.

2) Run an algorithm using the cached datasets

- Coming Soon - Analyze datasets and store output (generated csvs)
  in s3 and redis.
- Coming Soon - Make predictions using an analyzed dataset

**Supported Actions**

#.  **Algorithm-Ready** Datasets

    Algo-ready datasets were created by the Algorithm Extraction API.

    You can tune algorithm performance by deriving your own algorithm
    from the `analysis_engine.algo.BaseAlgo <ht
    tps://github.com/AlgoTraders/stock-analysis-engine/blob/master/ana
    lysis_engine/algo.py>`__ and then loading the dataset from
    s3, redis or a file by passing the correct arguments.

    Command line actions:

    - **Extract** algorithm-ready datasets out of redis to a file

        ::

            sa.py -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

    - **View** algorithm-ready datasets in a file

        ::

            sa.py -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

    - **Restore** algorithm-ready datasets from a file to redis

        This also works as a backup tool for archiving an entire
        single ticker dataset from redis to a single file. (zlib compression
        is code-complete but has not been debugged end-to-end)

        ::

            sa.py -t SPY -L ~/SPY-$(date +"%Y-%m-%d").json

        .. warning:: if the output redis key or s3 key already exists, this
            process will overwrite the previously stored values

#.  **Run an Algorithm**

    Please refer to the `included Minute Algorithm <https://github.com/Algo
    Traders/stock-analysis-engine/blob/master/analysis_engine/mocks/e
    xample_algo_minute.py>`__ for an up to date reference.

    ::

        sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

"""

import os
import sys
import datetime
import argparse
import analysis_engine.charts as ae_charts
import analysis_engine.iex.extract_df_from_redis as extract_utils
import analysis_engine.run_algo as run_algo
import analysis_engine.show_dataset as show_dataset
import analysis_engine.restore_dataset as restore_dataset
import analysis_engine.run_custom_algo as run_custom_algo
import analysis_engine.work_tasks.prepare_pricing_dataset \
    as prepare_pricing_dataset
from celery import signals
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.work_tasks.get_celery_app import get_celery_app
from analysis_engine.api_requests import build_prepare_dataset_request
from analysis_engine.consts import SA_MODE_PREPARE
from analysis_engine.consts import SA_MODE_EXTRACT
from analysis_engine.consts import SA_MODE_SHOW_DATASET
from analysis_engine.consts import SA_MODE_RESTORE_REDIS_DATASET
from analysis_engine.consts import SA_MODE_RUN_ALGO
from analysis_engine.consts import LOG_CONFIG_PATH
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import WORKER_BROKER_URL
from analysis_engine.consts import WORKER_BACKEND_URL
from analysis_engine.consts import WORKER_CELERY_CONFIG_MODULE
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
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import PLOT_ACTION_SHOW
from analysis_engine.consts import PLOT_ACTION_SAVE_TO_S3
from analysis_engine.consts import PLOT_ACTION_SAVE_AS_FILE
from analysis_engine.consts import IEX_MINUTE_DATE_FORMAT
from analysis_engine.consts import DEFAULT_SERIALIZED_DATASETS
from analysis_engine.consts import SA_DATASET_TYPE_ALGO_READY
from analysis_engine.consts import get_status
from analysis_engine.consts import ppj
from analysis_engine.consts import is_celery_disabled
from analysis_engine.utils import utc_now_str


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


log = build_colorized_logger(
    name='sa',
    log_config_path=LOG_CONFIG_PATH)


def restore_missing_dataset_values_from_algo_ready_file(
        ticker,
        path_to_file,
        redis_address,
        redis_password,
        redis_db=REDIS_DB,
        output_redis_db=None,
        compress=False,
        encoding='utf-8',
        dataset_type=SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=DEFAULT_SERIALIZED_DATASETS,
        show_summary=True):
    """restore_missing_dataset_values_from_algo_ready_file

    restore missing dataset nodes in redis from an algorithm-ready
    dataset file on disk - use this to restore redis from scratch

    :param ticker: string ticker
    :param path_to_file: string path to file on disk
    :param redis_address: redis server endpoint adddress with
        format ``host:port``
    :param redis_password: optional - string password for redis
    :param redis_db: redis db (default is ``REDIS_DB``)
    :param output_redis_db: optional - integer for different
        redis database (default is ``None``)
    :param compress: contents in algorithm-ready file are
        compressed (default is ``False``)
    :param encoding: byte encoding of algorithm-ready file
        (default is ``utf-8``)
    :param dataset_type: optional - dataset type
        (default is ``SA_DATASET_TYPE_ALGO_READY``)
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    :param show_summary: optional - show a summary of the algorithm-ready
        dataset using ``analysis_engine.show_dataset.show_dataset``
        (default is ``True``)
    """
    if not os.path.exists(path_to_file):
        log.error(
            'missing file={} for restore'.format(
                path_to_file))
        return

    if dataset_type == SA_DATASET_TYPE_ALGO_READY:
        log.info(
            'restore start - load dataset from file={}'.format(
                path_to_file))
    else:
        log.error(
            'restore dataset unsupported type={} for file={}'.format(
                dataset_type,
                path_to_file))
        return

    if not output_redis_db:
        output_redis_db = redis_db

    restore_dataset.restore_dataset(
        show_summary=show_summary,
        path_to_file=path_to_file,
        compress=compress,
        encoding=encoding,
        dataset_type=dataset_type,
        serialize_datasets=serialize_datasets,
        redis_address=redis_address,
        redis_password=redis_password,
        redis_db=redis_db,
        redis_output_db=output_redis_db,
        verbose=False)
    log.info(
        'restore done - dataset in file={}'.format(
            path_to_file))
# end of restore_missing_dataset_values_from_algo_ready_file


def examine_dataset_in_file(
        path_to_file,
        compress=False,
        encoding='utf-8',
        ticker=None,
        dataset_type=SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=DEFAULT_SERIALIZED_DATASETS,):
    """examine_dataset_in_file

    Show the internal dataset dictionary structure in dataset file

    :param path_to_file: path to file
    :param compress: optional - boolean flag for decompressing
        the contents of the ``path_to_file`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding
    :param ticker: optional - string ticker symbol
        to verify is in the dataset
    :param dataset_type: optional - dataset type
        (default is ``SA_DATASET_TYPE_ALGO_READY``)
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    """
    if dataset_type == SA_DATASET_TYPE_ALGO_READY:
        log.info(
            'show start - load dataset from file={}'.format(
                path_to_file))
    else:
        log.error(
            'show unsupported dataset type={} for file={}'.format(
                dataset_type,
                path_to_file))
        return
    show_dataset.show_dataset(
        path_to_file=path_to_file,
        compress=compress,
        encoding=encoding,
        dataset_type=dataset_type,
        serialize_datasets=serialize_datasets)
    log.info(
        'show done - dataset in file={}'.format(
            path_to_file))
# end of examine_dataset_in_file


def extract_ticker_to_a_file_using_an_algo(
        ticker,
        extract_to_file):
    """extract_ticker_to_a_file_using_an_algo

    Extract all ``ticker`` datasets to a local file

    :param ticker: ticker to find
    :param extract_to_file: save all datasets to this
        file on disk
    """
    log.info(
        'extract start - running algo - {} to {}'.format(
            ticker,
            extract_to_file))
    algo_res = run_algo.run_algo(
        label='sa',
        ticker=ticker,
        start_date='2018-01-01 08:00:00',
        end_date=utc_now_str())
    if algo_res['status'] != SUCCESS:
        log.error(
            'extract run - {} - {}'.format(
                get_status(status=algo_res['status']),
                algo_res['err']))
        return
    log.info(
        'extract start - building dataset - {} to {}'.format(
            ticker,
            extract_to_file))
    algo = algo_res['rec'].get(
        'algo',
        None)
    if not algo:
        log.error(
            'extract missing created algo object - {} - {}'.format(
                get_status(status=algo_res['status']),
                algo_res['err']))
        return
    publish_status, output_file = algo.publish_input_datasets(
        output_file=extract_to_file)
    if not os.path.exists(output_file):
        log.error(
            'extract failed to save datasets to file={} '
            'with status {}'.format(
                extract_to_file,
                get_status(status=publish_status)))
        return
    log.info(
        'extract done - {} saved to {} - {}'.format(
            ticker,
            extract_to_file,
            get_status(status=publish_status)))
# end of extract_ticker_to_a_file_using_an_algo


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
        '-e',
        help=(
            'file path to extract an '
            'algorithm-ready datasets from redis'),
        required=False,
        dest='extract_to_file')
    parser.add_argument(
        '-l',
        help=(
            'show dataset in this file'),
        required=False,
        dest='show_from_file')
    parser.add_argument(
        '-L',
        help=(
            'restore an algorithm-ready dataset file back into redis'),
        required=False,
        dest='restore_algo_file')
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
        '-J',
        help=(
            'plot action - after preparing you can use: '
            '-J show to open the image (good for debugging)'),
        required=False,
        dest='plot_action')
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
        '-G',
        help=(
            'optional - s3 region name'),
        required=False,
        dest='s3_region_name')
    parser.add_argument(
        '-g',
        help=(
            'Path to a custom algorithm module file '
            'on disik. This module must have a single '
            'class that inherits from: '
            'https://github.com/AlgoTraders/stock-ana'
            'lysis-engine/blob/master/'
            'analysis_engine/algo.py Additionally you '
            'can find the Example-Minute-Algorithm here: '
            'https://github.com/AlgoTraders/stock-anal'
            'ysis-engine/blob/master/analysis_engine/mocks/'
            'example_algo_minute.py'),
        required=False,
        dest='run_algo_in_file')
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
            'optional - redis database number (0 by default)'),
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
    plot_action = PLOT_ACTION_SHOW
    ticker = TICKER
    ticker_id = TICKER_ID
    ssl_options = SSL_OPTIONS
    transport_options = TRANSPORT_OPTIONS
    broker_url = WORKER_BROKER_URL
    backend_url = WORKER_BACKEND_URL
    celery_config_module = WORKER_CELERY_CONFIG_MODULE
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

    extract_to_file = None
    show_from_file = None
    restore_algo_file = None

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
    if args.plot_action:
        if str(args.plot_action).lower() == 'show':
            plot_action = PLOT_ACTION_SHOW
        elif str(args.plot_action).lower() == 's3':
            plot_action = PLOT_ACTION_SAVE_TO_S3
        elif str(args.plot_action).lower() == 'save':
            plot_action = PLOT_ACTION_SAVE_AS_FILE
        else:
            plot_action = PLOT_ACTION_SHOW
            log.warning(
                'unsupported plot_action: {}'.format(
                    args.plot_action))

    if args.debug:
        debug = True

    if args.extract_to_file:
        extract_to_file = args.extract_to_file
        mode = SA_MODE_EXTRACT
    if args.show_from_file:
        show_from_file = args.show_from_file
        mode = SA_MODE_SHOW_DATASET
    if args.restore_algo_file:
        restore_algo_file = args.restore_algo_file
        mode = SA_MODE_RESTORE_REDIS_DATASET
    if args.run_algo_in_file:
        mode = SA_MODE_RUN_ALGO

    valid = False
    required_task = False
    work = None
    task_name = None
    work = {}
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
        valid = True
        required_task = True
    elif mode == SA_MODE_EXTRACT:
        extract_ticker_to_a_file_using_an_algo(
            ticker=ticker,
            extract_to_file=extract_to_file)
        log.info(
            'done extracting {} dataset and saving to file={}'.format(
                ticker,
                show_from_file))
        sys.exit(0)
    elif mode == SA_MODE_SHOW_DATASET:
        examine_dataset_in_file(
            ticker=ticker,
            path_to_file=show_from_file)
        log.info(
            'done showing {} dataset from file={}'.format(
                ticker,
                show_from_file))
        sys.exit(0)
    elif mode == SA_MODE_RESTORE_REDIS_DATASET:
        restore_missing_dataset_values_from_algo_ready_file(
            ticker=ticker,
            path_to_file=restore_algo_file,
            redis_address=redis_address,
            redis_password=redis_password,
            redis_db=redis_db,
            output_redis_db=redis_db,
            dataset_type=SA_DATASET_TYPE_ALGO_READY,
            serialize_datasets=DEFAULT_SERIALIZED_DATASETS)
        log.info(
            'done restoring {} dataset from file={} into redis_db={}'.format(
                ticker,
                restore_algo_file,
                redis_db))
        sys.exit(0)
    elif mode == SA_MODE_RUN_ALGO:
        use_balance = 5000.0
        use_commission = 6.0
        use_start_date = None
        use_end_date = None
        use_config_file = None
        use_name = 'myalgo'

        if not os.path.exists(args.run_algo_in_file):
            log.error(
                'missing algorithm module file: {}'.format(
                    args.run_algo_in_file))
            sys.exit(1)

        algo_res = run_custom_algo.run_custom_algo(
            mod_path=args.run_algo_in_file,
            ticker=ticker,
            balance=use_balance,
            commission=use_commission,
            start_date=use_start_date,
            end_date=use_end_date,
            config_file=use_config_file,
            name=use_name)
        if args.debug:
            if algo_res['status'] == SUCCESS:
                log.info(
                    '{} - done running {} algo.name={} from '
                    'file {} results: {}'.format(
                        get_status(status=algo_res['status']),
                        ticker,
                        algo_res['algo'].name,
                        args.run_algo_in_file,
                        ppj(algo_res['rec'])))
            else:
                log.error(
                    '{} - done running {} algo.name={} from '
                    'file {} results: {}'.format(
                        get_status(status=algo_res['status']),
                        ticker,
                        algo_res['algo'].name,
                        args.run_algo_in_file,
                        ppj(algo_res['rec'])))
        else:
            if algo_res['status'] == SUCCESS:
                log.info(
                    '{} - done running {} algo.name={} from '
                    'file {} algorithm performance history '
                    'records: {}'.format(
                        get_status(status=algo_res['status']),
                        ticker,
                        algo_res['algo'].name,
                        args.run_algo_in_file,
                        len(algo_res['rec']['history'])))
            else:
                log.error(
                    '{} - done running {} algo.name={} from '
                    'file {} algorithm performance history '
                    'records: {}'.format(
                        get_status(status=algo_res['status']),
                        ticker,
                        algo_res['algo'].name,
                        args.run_algo_in_file,
                        len(algo_res['rec']['history'])))
        sys.exit(0)
    # end of handling mode-specific arg assignments

    # sanity checking the work and task are valid
    if not valid:
        log.error(
            'usage error: missing a supported mode: '
            '-f (for prepare a dataset) ')
        sys.exit(1)
    if required_task and not task_name:
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

        if debug:
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
                'done - result '
                'task={} status={} '
                'err={} label={}'.format(
                    task_name,
                    get_status(status=task_res['status']),
                    task_res['err'],
                    work['label']))

        if task_res['status'] == SUCCESS:
            image_res = None
            label = work['label']
            ticker = work['ticker']
            if plot_action == PLOT_ACTION_SHOW:
                log.info(
                    'showing plot')
                """
                minute_key = '{}_minute'.format(
                    redis_key)
                minute_df_res = build_df.build_df_from_redis(
                    label=label',
                    address=redis_address,
                    db=redis_db,
                    key=minute_key)

                minute_df = None
                if (
                        minute_df_res['status'] == SUCCESS
                        and minute_df_res['rec']['valid_df']):
                    minute_df = minute_df_res['rec']['data']
                    print(minute_df.columns.values)
                    column_list = [
                        'close',
                        'date'
                    ]
                """
                today_str = datetime.datetime.now().strftime(
                    '%Y-%m-%d')
                extract_req = work
                extract_req['redis_key'] = '{}_minute'.format(
                    work['redis_key'])
                extract_status, minute_df = \
                    extract_utils.extract_minute_dataset(
                        work_dict=work)
                if extract_status == SUCCESS:
                    log.info(
                        '{} - ticker={} creating chart date={}'.format(
                            label,
                            ticker,
                            today_str))
                    """
                    Plot Pricing with the Volume Overlay:
                    """
                    image_res = ae_charts.plot_overlay_pricing_and_volume(
                        log_label=label,
                        ticker=ticker,
                        date_format=IEX_MINUTE_DATE_FORMAT,
                        df=minute_df,
                        show_plot=True)

                    """
                    Plot the High-Low-Open-Close Pricing:
                    """
                    """
                    image_res = ae_charts.plot_hloc_pricing(
                        log_label=label,
                        ticker=ticker,
                        title='{} - Minute Pricing - {}'.format(
                            ticker,
                            today_str),
                        df=minute_df,
                        show_plot=True)
                    """

                    """
                    Plot by custom columns in the DataFrame
                    """
                    """
                    column_list = minute_df.columns.values
                    column_list = [
                        'date',
                        'close',
                        'high',
                        'low',
                        'open'
                    ]
                    image_res = ae_charts.plot_df(
                        log_label=label,
                        title='Pricing Title',
                        column_list=column_list,
                        df=minute_df,
                        xcol='date',
                        xlabel='Date',
                        ylabel='Pricing',
                        show_plot=True)
                    """
            elif plot_action == PLOT_ACTION_SAVE_TO_S3:
                log.info(
                    'coming soon - support to save to s3')
            elif plot_action == PLOT_ACTION_SAVE_AS_FILE:
                log.info(
                    'coming soon - support to save as file')
            if image_res:
                log.info(
                    '{} show plot - status={} err={}'.format(
                        label,
                        get_status(image_res['status']),
                        image_res['err']))
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
            path_to_config_module=celery_config_module,
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

# end of run_sa_tool


if __name__ == '__main__':
    run_sa_tool()
