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
    tps://github.com/AlgoTraders/stock-analysis-engine/blob/master/
    analysis_engine/algo.py>`__ and then loading the dataset from
    s3, redis or a file by passing the correct arguments.

    Command line actions:

    - **Extract** algorithm-ready datasets out of redis to a file

        ::

            sa -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

    - **View** algorithm-ready datasets in a file

        ::

            sa -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

    - **Restore** algorithm-ready datasets from a file to redis

        This also works as a backup tool for archiving an entire
        single ticker dataset from redis to a single file. (zlib compression
        is code-complete but has not been debugged end-to-end)

        ::

            sa -t SPY -L ~/SPY-$(date +"%Y-%m-%d").json

        .. warning:: if the output redis key or s3 key already exists, this
            process will overwrite the previously stored values

#.  **Run an Algorithm**

    Please refer to the `included Minute Algorithm <https://github.com/Algo
    Traders/stock-analysis-engine/blob/master/analysis_engine/mocks/e
    xample_algo_minute.py>`__ for an up to date reference.

    ::

        sa -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

"""

import os
import sys
import datetime
import argparse
import celery
import analysis_engine.consts as ae_consts
import analysis_engine.run_custom_algo as run_custom_algo
import analysis_engine.work_tasks.get_celery_app as get_celery_app
import analysis_engine.plot_trading_history as plot_trading_history
import analysis_engine.charts as ae_charts
import analysis_engine.iex.extract_df_from_redis as extract_utils
import analysis_engine.show_dataset as show_dataset
import analysis_engine.load_history_dataset_from_file as load_history
import analysis_engine.load_report_dataset_from_file as load_report
import analysis_engine.restore_dataset as restore_dataset
import analysis_engine.work_tasks.prepare_pricing_dataset as prep_dataset
import analysis_engine.api_requests as api_requests
import spylunking.log.setup_logging as log_utils


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@celery.signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


log = log_utils.build_colorized_logger(
    name='sa',
    log_config_path=ae_consts.LOG_CONFIG_PATH)


def restore_missing_dataset_values_from_algo_ready_file(
        ticker,
        path_to_file,
        redis_address,
        redis_password,
        redis_db=ae_consts.REDIS_DB,
        output_redis_db=None,
        compress=True,
        encoding='utf-8',
        dataset_type=ae_consts.SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,
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
        compressed (default is ``True``)
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
        log.error(f'missing file={path_to_file} for restore')
        return

    if dataset_type == ae_consts.SA_DATASET_TYPE_ALGO_READY:
        log.info(f'restore start - load dataset from file={path_to_file}')
    else:
        log.error(
            'restore dataset unsupported '
            f'type={dataset_type} for file={path_to_file}')
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
    log.info(f'restore done - dataset in file={path_to_file}')
# end of restore_missing_dataset_values_from_algo_ready_file


def examine_dataset_in_file(
        path_to_file,
        compress=False,
        encoding='utf-8',
        ticker=None,
        dataset_type=ae_consts.SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,):
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
    if dataset_type == ae_consts.SA_DATASET_TYPE_ALGO_READY:
        log.info(f'show start - load dataset from file={path_to_file}')
        show_dataset.show_dataset(
            path_to_file=path_to_file,
            compress=compress,
            encoding=encoding,
            dataset_type=dataset_type,
            serialize_datasets=serialize_datasets)
        log.info(f'show done - dataset in file={path_to_file}')
    elif dataset_type == ae_consts.SA_DATASET_TYPE_TRADING_HISTORY:
        log.info(
            'load trading history dataset '
            f'from file={path_to_file}')
        trading_history_dict = load_history.load_history_dataset_from_file(
            path_to_file=path_to_file,
            compress=compress,
            encoding=encoding)
        history_df = trading_history_dict[ticker]

        first_date = history_df['date'].iloc[0]
        end_date = history_df['date'].iloc[-1]
        title = (
            f'Trading History {ticker} for Algo '
            f'{trading_history_dict["algo_name"]}\n'
            f'Backtest dates from {first_date} to {end_date}')
        xcol = 'date'
        xlabel = f'Dates vs {trading_history_dict["algo_name"]} values'
        ylabel = (
            'Algo Values from columns:\n'
            f'{list(history_df.columns.values)}')
        df_filter = (history_df['close'] > 0.01)

        # set default hloc columns:
        red = 'close'
        blue = 'low'
        green = 'high'
        orange = 'open'

        log.info(
            'available columns to plot in dataset: '
            f'{ae_consts.ppj(list(history_df.columns.values))}')

        plot_trading_history.plot_trading_history(
            title=title,
            df=history_df,
            red=red,
            blue=blue,
            green=green,
            orange=orange,
            date_col=xcol,
            xlabel=xlabel,
            ylabel=ylabel,
            df_filter=df_filter,
            show_plot=True,
            dropna_for_all=False)
    elif dataset_type == ae_consts.SA_DATASET_TYPE_TRADING_REPORT:
        log.info(
            'load trading performance report dataset '
            f'from file={path_to_file}')
        trading_report_dict = load_report.load_report_dataset_from_file(
            path_to_file=path_to_file,
            compress=compress,
            encoding=encoding)
        print(trading_report_dict)
    else:
        log.error(
            f'show unsupported dataset type={dataset_type} '
            f'for file={path_to_file}')
        return
# end of examine_dataset_in_file


def run_sa_tool():
    """run_sa_tool

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
        dest='algo_extract_loc')
    parser.add_argument(
        '-l',
        help=(
            'show dataset in this file'),
        required=False,
        dest='show_from_file')
    parser.add_argument(
        '-H',
        help=(
            'show trading history dataset in this file'),
        required=False,
        dest='show_history_from_file')
    parser.add_argument(
        '-E',
        help=(
            'show trading performance report dataset in this file'),
        required=False,
        dest='show_report_from_file')
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
        '-J',
        help=(
            'plot action - after preparing you can use: '
            '-J show to open the image (good for debugging)'),
        required=False,
        dest='plot_action')
    parser.add_argument(
        '-b',
        help=(
            'run a backtest using the dataset in '
            'a file path/s3 key/redis key formats: '
            'file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
            's3://algoready/SPY-latest.json or '
            'redis:SPY-latest'),
        required=False,
        dest='backtest_loc')
    parser.add_argument(
        '-B',
        help=(
            'optional - broker url for Celery'),
        required=False,
        dest='broker_url')
    parser.add_argument(
        '-C',
        help=(
            'optional - broker url for Celery'),
        required=False,
        dest='backend_url')
    parser.add_argument(
        '-w',
        help=(
            'optional - flag for publishing an algorithm job '
            'using Celery to the ae workers'),
        required=False,
        dest='run_on_engine',
        action='store_true')
    parser.add_argument(
        '-k',
        help=(
            'optional - s3 access key'),
        required=False,
        dest='s3_access_key')
    parser.add_argument(
        '-K',
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
        '-Z',
        help=(
            'optional - s3 secure: default False'),
        required=False,
        dest='s3_secure')
    parser.add_argument(
        '-s',
        help=(
            'optional - start date: YYYY-MM-DD'),
        required=False,
        dest='start_date')
    parser.add_argument(
        '-n',
        help=(
            'optional - end date: YYYY-MM-DD'),
        required=False,
        dest='end_date')
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
            'on disk. This module must have a single '
            'class that inherits from: '
            'https://github.com/AlgoTraders/stock-analysis-engine/'
            'blob/master/'
            'analysis_engine/algo.py Additionally you '
            'can find the Example-Minute-Algorithm here: '
            'https://github.com/AlgoTraders/stock-analysis-engine/'
            'blob/master/analysis_engine/mocks/'
            'example_algo_minute.py'),
        required=False,
        dest='run_algo_in_file')
    parser.add_argument(
        '-p',
        help=(
            'optional - s3 bucket/file for trading history'),
        required=False,
        dest='algo_history_loc')
    parser.add_argument(
        '-o',
        help=(
            'optional - s3 bucket/file for trading performance report'),
        required=False,
        dest='algo_report_loc')
    parser.add_argument(
        '-r',
        help=(
            'optional - redis_address format: <host:port>'),
        required=False,
        dest='redis_address')
    parser.add_argument(
        '-R',
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
            'optional - algorithm config_file path for setting '
            'up internal algorithm trading strategies and '
            'indicators'),
        required=False,
        dest='config_file')
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
    plot_action = ae_consts.PLOT_ACTION_SHOW
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    ssl_options = ae_consts.SSL_OPTIONS
    transport_options = ae_consts.TRANSPORT_OPTIONS
    broker_url = ae_consts.WORKER_BROKER_URL
    backend_url = ae_consts.WORKER_BACKEND_URL
    path_to_config_module = ae_consts.WORKER_CELERY_CONFIG_MODULE
    include_tasks = ae_consts.INCLUDE_TASKS
    s3_access_key = ae_consts.S3_ACCESS_KEY
    s3_secret_key = ae_consts.S3_SECRET_KEY
    s3_region_name = ae_consts.S3_REGION_NAME
    s3_address = ae_consts.S3_ADDRESS
    s3_secure = ae_consts.S3_SECURE
    s3_bucket_name = ae_consts.S3_BUCKET
    s3_key = ae_consts.S3_KEY
    redis_address = ae_consts.REDIS_ADDRESS
    redis_key = ae_consts.REDIS_KEY
    redis_password = ae_consts.REDIS_PASSWORD
    redis_db = ae_consts.REDIS_DB
    redis_expire = ae_consts.REDIS_EXPIRE
    dataset_type = ae_consts.SA_DATASET_TYPE_ALGO_READY
    serialize_datasets = ae_consts.DEFAULT_SERIALIZED_DATASETS
    output_redis_key = None
    output_s3_bucket = None
    output_s3_key = None
    ignore_columns = None
    compress = False
    encoding = 'utf-8'
    slack_enabled = False
    slack_code_block = False
    slack_full_width = False
    verbose = False
    debug = False

    redis_serializer = 'json'
    redis_encoding = 'utf-8'
    output_redis_key = None
    output_s3_bucket = None
    output_s3_key = None
    s3_enabled = True
    redis_enabled = True
    ignore_columns = None
    debug = False

    run_on_engine = False
    show_from_file = None
    show_history_from_file = None
    show_report_from_file = None
    restore_algo_file = None
    backtest_loc = None
    use_custom_algo = False
    algo_history_loc = 's3://algohistory'
    algo_report_loc = 's3://algoreport'
    algo_extract_loc = 's3://algoready'

    use_balance = 5000.0
    use_commission = 6.0
    auto_fill = True
    use_start_date = None
    use_end_date = None
    use_config_file = None
    use_name = 'myalgo'

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
        s3_enabled = True
    if args.s3_secure:
        s3_secure = args.s3_secure
    if args.s3_bucket_name:
        s3_bucket_name = args.s3_bucket_name
    if args.keyname:
        s3_key = args.keyname
        redis_key = args.keyname
    if args.redis_address:
        redis_address = args.redis_address
    if args.redis_db:
        redis_db = args.redis_db
    if args.redis_expire:
        redis_expire = args.redis_expire
    if args.prepare_mode:
        mode = ae_consts.SA_MODE_PREPARE
    if args.ignore_columns:
        ignore_columns_org = args.ignore_columns
        ignore_columns = ignore_columns_org.split(",")
    if args.plot_action:
        if str(args.plot_action).lower() == 'show':
            plot_action = ae_consts.PLOT_ACTION_SHOW
        elif str(args.plot_action).lower() == 's3':
            plot_action = ae_consts.PLOT_ACTION_SAVE_TO_S3
        elif str(args.plot_action).lower() == 'save':
            plot_action = ae_consts.PLOT_ACTION_SAVE_AS_FILE
        else:
            plot_action = ae_consts.PLOT_ACTION_SHOW
            log.warning(f'unsupported plot_action: {args.plot_action}')

    if args.debug:
        debug = True

    if args.algo_extract_loc:
        mode = ae_consts.SA_MODE_EXTRACT
    if args.show_from_file:
        show_from_file = args.show_from_file
        mode = ae_consts.SA_MODE_SHOW_DATASET
    if args.show_history_from_file:
        show_history_from_file = args.show_history_from_file
        mode = ae_consts.SA_MODE_SHOW_HISTORY_DATASET
    if args.show_report_from_file:
        show_report_from_file = args.show_report_from_file
        mode = ae_consts.SA_MODE_SHOW_REPORT_DATASET
    if args.restore_algo_file:
        restore_algo_file = args.restore_algo_file
        mode = ae_consts.SA_MODE_RESTORE_REDIS_DATASET
    if args.run_algo_in_file:
        mode = ae_consts.SA_MODE_RUN_ALGO
    if args.backtest_loc:
        mode = ae_consts.SA_MODE_RUN_ALGO
    if args.start_date:
        try:
            use_start_date = f'{str(args.start_date)} 00:00:00'
            datetime.datetime.strptime(
                args.start_date,
                ae_consts.COMMON_DATE_FORMAT)
        except Exception as e:
            msg = (
                'please use a start date formatted as: '
                f'{ae_consts.COMMON_DATE_FORMAT}\n'
                f'error was: {e}')
            log.error(msg)
            sys.exit(1)
        # end of testing for a valid date
    # end of args.start_date
    if args.end_date:
        try:
            use_end_date = f'{str(args.end_date)} 00:00:00'
            datetime.datetime.strptime(
                args.end_date,
                ae_consts.COMMON_DATE_FORMAT)
        except Exception as e:
            msg = (
                'please use an end date formatted as: '
                f'{ae_consts.COMMON_DATE_FORMAT}\n'
                f'error was: {e}')
            log.error(msg)
            sys.exit(1)
        # end of testing for a valid date
    # end of args.end_date
    if args.config_file:
        use_config_file = args.config_file
        if not os.path.exists(use_config_file):
            log.error(
                f'Failed: unable to find config file: -c {use_config_file}')
            sys.exit(1)

    config_dict = None
    load_from_s3_bucket = None
    load_from_s3_key = None
    load_from_redis_key = None
    load_from_file = None
    load_compress = False
    load_publish = True
    load_config = None
    report_redis_key = None
    report_s3_bucket = None
    report_s3_key = None
    report_file = None
    report_compress = False
    report_publish = True
    report_config = None
    history_redis_key = None
    history_s3_bucket = None
    history_s3_key = None
    history_file = None
    history_compress = False
    history_publish = True
    history_config = None
    extract_redis_key = None
    extract_s3_bucket = None
    extract_s3_key = None
    extract_file = None
    extract_save_dir = None
    extract_compress = False
    extract_publish = True
    extract_config = None
    publish_to_slack = False
    publish_to_s3 = True
    publish_to_redis = True
    use_timeseries = 'day'
    use_trade_strategy = 'count'

    valid = False
    required_task = False
    work = None
    task_name = None
    work = {}
    path_to_tasks = 'analysis_engine.work_tasks'
    if mode == ae_consts.SA_MODE_PREPARE:
        task_name = (
            f'{path_to_tasks}.'
            'prepare_pricing_dataset.prepare_pricing_dataset')
        work = api_requests.build_prepare_dataset_request()
        if output_s3_key:
            work['prepared_s3_key'] = output_s3_key
        if output_s3_bucket:
            work['prepared_s3_bucket'] = output_s3_bucket
        if output_redis_key:
            work['prepared_redis_key'] = output_redis_key
        work['ignore_columns'] = ignore_columns
        valid = True
        required_task = True
    elif mode == ae_consts.SA_MODE_EXTRACT:
        if args.algo_extract_loc:
            algo_extract_loc = args.algo_extract_loc
            if ('file:/' not in algo_extract_loc and
                    's3://' not in algo_extract_loc and
                    'redis://' not in algo_extract_loc):
                log.error(
                    'invalid -e <extract_to_file_or_s3_key_or_redis_key> '
                    'specified. please use either: '
                    '-e file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-e s3://algoready/SPY-latest.json or '
                    '-e redis://SPY-latest')
                sys.exit(1)
            if 's3://' in algo_extract_loc:
                extract_s3_bucket = algo_extract_loc.split('/')[-2]
                extract_s3_key = algo_extract_loc.split('/')[-1]
            elif 'redis://' in algo_extract_loc:
                extract_redis_key = algo_extract_loc.split('/')[-1]
            elif 'file:/' in algo_extract_loc:
                extract_file = algo_extract_loc.split(':')[-1]
        # end of parsing supported transport for loading

        use_custom_algo = True
    elif mode == ae_consts.SA_MODE_SHOW_DATASET:
        examine_dataset_in_file(
            ticker=ticker,
            path_to_file=show_from_file)
        log.info(
            f'done showing {ticker} dataset from file={show_from_file}')
        sys.exit(0)
    elif mode == ae_consts.SA_MODE_SHOW_HISTORY_DATASET:
        examine_dataset_in_file(
            ticker=ticker,
            dataset_type=ae_consts.SA_DATASET_TYPE_TRADING_HISTORY,
            path_to_file=show_history_from_file)
        log.info(
            f'done showing trading history {ticker} dataset from '
            f'file={show_from_file}')
        sys.exit(0)
    elif mode == ae_consts.SA_MODE_SHOW_REPORT_DATASET:
        examine_dataset_in_file(
            ticker=ticker,
            dataset_type=ae_consts.SA_DATASET_TYPE_TRADING_REPORT,
            path_to_file=show_report_from_file)
        log.info(
            f'done showing trading performance report {ticker} dataset from '
            f'file={show_from_file}')
        sys.exit(0)
    elif mode == ae_consts.SA_MODE_RESTORE_REDIS_DATASET:
        restore_missing_dataset_values_from_algo_ready_file(
            ticker=ticker,
            path_to_file=restore_algo_file,
            redis_address=redis_address,
            redis_password=redis_password,
            redis_db=redis_db,
            output_redis_db=redis_db,
            dataset_type=ae_consts.SA_DATASET_TYPE_ALGO_READY,
            serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS)
        log.info(
            f'done restoring {ticker} dataset from file={restore_algo_file} '
            f'into redis_db={redis_db}')
        sys.exit(0)
    elif mode == ae_consts.SA_MODE_RUN_ALGO:
        if args.run_algo_in_file:
            if not os.path.exists(args.run_algo_in_file):
                log.error(
                    f'missing algorithm module file: {args.run_algo_in_file}')
                sys.exit(1)

        if args.backtest_loc:
            backtest_loc = args.backtest_loc
            if ('file:/' not in backtest_loc and
                    's3://' not in backtest_loc and
                    'redis://' not in backtest_loc):
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    f'{backtest_loc} '
                    'please use either: '
                    '-b file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-b s3://algoready/SPY-latest.json or '
                    '-b redis://SPY-latest')
                sys.exit(1)
            if 's3://' in backtest_loc:
                load_from_s3_bucket = backtest_loc.split('/')[-2]
                load_from_s3_key = backtest_loc.split('/')[-1]
            elif 'redis://' in backtest_loc:
                load_from_redis_key = backtest_loc.split('/')[-1]
            elif 'file:/' in backtest_loc:
                load_from_file = backtest_loc.split(':')[-1]
            load_publish = True
        # end of parsing supported transport - loading an algo-ready

        if args.algo_history_loc:
            algo_history_loc = args.algo_history_loc
            if ('file:/' not in algo_history_loc and
                    's3://' not in algo_history_loc and
                    'redis://' not in algo_history_loc):
                log.error(
                    'invalid -p <backtest dataset file> specified. '
                    f'{algo_history_loc} '
                    'please use either: '
                    '-p file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-p s3://algoready/SPY-latest.json or '
                    '-p redis://SPY-latest')
                sys.exit(1)
            if 's3://' in algo_history_loc:
                history_s3_bucket = algo_history_loc.split('/')[-2]
                history_s3_key = algo_history_loc.split('/')[-1]
            elif 'redis://' in algo_history_loc:
                history_redis_key = algo_history_loc.split('/')[-1]
            elif 'file:/' in algo_history_loc:
                history_file = algo_history_loc.split(':')[-1]
            history_publish = True
        # end of parsing supported transport - trading history

        if args.algo_report_loc:
            algo_report_loc = args.algo_report_loc
            if ('file:/' not in algo_report_loc and
                    's3://' not in algo_report_loc and
                    'redis://' not in algo_report_loc):
                log.error(
                    'invalid -o <backtest dataset file> specified. '
                    f'{algo_report_loc} '
                    'please use either: '
                    '-o file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-o s3://algoready/SPY-latest.json or '
                    '-o redis://SPY-latest')
                sys.exit(1)
            if 's3://' in algo_report_loc:
                report_s3_bucket = algo_report_loc.split('/')[-2]
                report_s3_key = algo_report_loc.split('/')[-1]
            elif 'redis://' in algo_report_loc:
                report_redis_key = algo_report_loc.split('/')[-1]
            elif 'file:/' in algo_report_loc:
                report_file = algo_report_loc.split(':')[-1]
            report_publish = True
        # end of parsing supported transport - trading performance report

        if args.algo_extract_loc:
            algo_extract_loc = args.algo_extract_loc
            if ('file:/' not in algo_extract_loc and
                    's3://' not in algo_extract_loc and
                    'redis://' not in algo_extract_loc):
                log.error(
                    'invalid -e <backtest dataset file> specified. '
                    f'{algo_extract_loc} '
                    'please use either: '
                    '-e file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-e s3://algoready/SPY-latest.json or '
                    '-e redis://SPY-latest')
                sys.exit(1)
            if 's3://' in algo_extract_loc:
                extract_s3_bucket = algo_extract_loc.split('/')[-2]
                extract_s3_key = algo_extract_loc.split('/')[-1]
            elif 'redis://' in algo_extract_loc:
                extract_redis_key = algo_extract_loc.split('/')[-1]
            elif 'file:/' in algo_extract_loc:
                extract_file = algo_extract_loc.split(':')[-1]
            extract_publish = True
        # end of parsing supported transport - extract algorithm-ready

        use_custom_algo = True
    # end of set up for backtest

    if use_custom_algo:

        if args.run_on_engine:
            run_on_engine = True
            log.info('starting algo on the engine')
        else:
            log.info('starting algo')

        algo_res = run_custom_algo.run_custom_algo(
            mod_path=args.run_algo_in_file,
            ticker=ticker,
            balance=use_balance,
            commission=use_commission,
            start_date=use_start_date,
            end_date=use_end_date,
            config_file=use_config_file,
            name=use_name,
            auto_fill=auto_fill,
            config_dict=config_dict,
            load_from_s3_bucket=load_from_s3_bucket,
            load_from_s3_key=load_from_s3_key,
            load_from_redis_key=load_from_redis_key,
            load_from_file=load_from_file,
            load_compress=load_compress,
            load_publish=load_publish,
            load_config=load_config,
            report_redis_key=report_redis_key,
            report_s3_bucket=report_s3_bucket,
            report_s3_key=report_s3_key,
            report_file=report_file,
            report_compress=report_compress,
            report_publish=report_publish,
            report_config=report_config,
            history_redis_key=history_redis_key,
            history_s3_bucket=history_s3_bucket,
            history_s3_key=history_s3_key,
            history_file=history_file,
            history_compress=history_compress,
            history_publish=history_publish,
            history_config=history_config,
            extract_redis_key=extract_redis_key,
            extract_s3_bucket=extract_s3_bucket,
            extract_s3_key=extract_s3_key,
            extract_file=extract_file,
            extract_save_dir=extract_save_dir,
            extract_compress=extract_compress,
            extract_publish=extract_publish,
            extract_config=extract_config,
            publish_to_slack=publish_to_slack,
            publish_to_s3=publish_to_s3,
            publish_to_redis=publish_to_redis,
            dataset_type=dataset_type,
            serialize_datasets=serialize_datasets,
            compress=compress,
            encoding=encoding,
            redis_enabled=redis_enabled,
            redis_key=redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=s3_enabled,
            s3_key=s3_key,
            s3_address=s3_address,
            s3_bucket=s3_bucket_name,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=slack_enabled,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            dataset_publish_extract=extract_publish,
            dataset_publish_history=history_publish,
            dataset_publish_report=report_publish,
            run_on_engine=run_on_engine,
            auth_url=broker_url,
            backend_url=backend_url,
            include_tasks=include_tasks,
            ssl_options=ssl_options,
            transport_options=transport_options,
            path_to_config_module=path_to_config_module,
            timeseries=use_timeseries,
            trade_strategy=use_trade_strategy,
            verbose=verbose)

        show_label = f'algo.name={use_name}'
        show_extract = f'{algo_extract_loc}'
        show_history = f'{algo_history_loc}'
        show_report = f'{algo_report_loc}'
        base_label = (
            f'load={args.run_algo_in_file} extract={show_extract} '
            f'history={show_history} report={show_report}')
        show_label = (
            f'{ticker} running in engine '
            f'''task_id={algo_res['rec'].get(
                'task_id',
                'missing-task-id')} {base_label}''')
        if not run_on_engine:
            algo_trade_history_recs = algo_res['rec'].get(
                'history',
                [])
            show_label = (
                f'{ticker} algo.name={use_name} {base_label} '
                f'trade_history_len={len(algo_trade_history_recs)}')
        if args.debug:
            log.info(f'algo_res={algo_res}')
            if algo_res['status'] == ae_consts.SUCCESS:
                log.info(
                    f'{ae_consts.get_status(status=algo_res["status"])} - '
                    f'done running {show_label}')
            else:
                log.error(
                    f'{ae_consts.get_status(status=algo_res["status"])} - '
                    f'done running {show_label}')
        else:
            if algo_res['status'] == ae_consts.SUCCESS:
                log.info(
                    f'{ae_consts.get_status(status=algo_res["status"])} - '
                    f'done running {show_label}')
            else:
                log.error(
                    f'run_custom_algo returned error: {algo_res["err"]}')
                sys.exit(1)
        # end of running the custom algo handler

        if mode == ae_consts.SA_MODE_EXTRACT:
            log.info(f'done extracting dataset - {ticker}')
        elif mode == ae_consts.SA_MODE_RUN_ALGO:
            log.info(f'done running algo - {ticker}')

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
    work['label'] = f'ticker={ticker}'

    task_res = None
    if ae_consts.is_celery_disabled():
        work['celery_disabled'] = True
        log.debug(f'starting without celery work={ae_consts.ppj(work)}')
        if mode == ae_consts.SA_MODE_PREPARE:
            task_res = prep_dataset.prepare_pricing_dataset(
                work)

        if debug:
            log.info(
                f'done - result={ae_consts.ppj(task_res)} task={task_name} '
                f'status={ae_consts.get_status(status=task_res["status"])} '
                f'err={task_res["err"]} label={work["label"]}')
        else:
            log.info(
                f'done - result task={task_name} '
                f'status={ae_consts.get_status(status=task_res["status"])} '
                f'err={task_res["err"]} label={work["label"]}')

        if task_res['status'] == ae_consts.SUCCESS:
            image_res = None
            label = work['label']
            ticker = work['ticker']
            if plot_action == ae_consts.PLOT_ACTION_SHOW:
                log.info(
                    'showing plot')
                """
                minute_key = f'{redis_key}_minute'
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
                extract_req['redis_key'] = f'{work["redis_key"]}_minute'
                extract_status, minute_df = \
                    extract_utils.extract_minute_dataset(
                        work_dict=work)
                if extract_status == ae_consts.SUCCESS:
                    log.info(
                        f'{label} - ticker={ticker} creating chart '
                        f'date={today_str}')
                    """
                    Plot Pricing with the Volume Overlay:
                    """
                    image_res = ae_charts.plot_overlay_pricing_and_volume(
                        log_label=label,
                        ticker=ticker,
                        date_format=ae_consts.IEX_MINUTE_DATE_FORMAT,
                        df=minute_df,
                        show_plot=True)

                    """
                    Plot the High-Low-Open-Close Pricing:
                    """
                    """
                    image_res = ae_charts.plot_hloc_pricing(
                        log_label=label,
                        ticker=ticker,
                        title=f'{ticker} - Minute Pricing - {today_str}',
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
            elif plot_action == ae_consts.PLOT_ACTION_SAVE_TO_S3:
                log.info(
                    'coming soon - support to save to s3')
            elif plot_action == ae_consts.PLOT_ACTION_SAVE_AS_FILE:
                log.info(
                    'coming soon - support to save as file')
            if image_res:
                log.info(
                    f'{label} show plot - '
                    f'status={ae_consts.get_status(image_res["status"])} '
                    f'err={image_res["err"]}')
    else:
        log.info(f'connecting to broker={broker_url} backend={backend_url}')

        # Get the Celery app
        app = get_celery_app.get_celery_app(
            name=__name__,
            auth_url=broker_url,
            backend_url=backend_url,
            path_to_config_module=path_to_config_module,
            ssl_options=ssl_options,
            transport_options=transport_options,
            include_tasks=include_tasks)

        log.info(f'calling task={task_name} - work={ae_consts.ppj(work)}')
        job_id = app.send_task(
            task_name,
            (work,))
        log.info(f'calling task={task_name} - success job_id={job_id}')
    # end of if/else

# end of run_sa_tool


if __name__ == '__main__':
    run_sa_tool()
