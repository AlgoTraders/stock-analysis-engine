"""
Run an Algo

**Supported environment variables**

::

    export REDIS_ADDRESS="localhost:6379"
    export REDIS_DB="0"
    export S3_ADDRESS="localhost:9000"
    export S3_BUCKET="dev"
    export AWS_ACCESS_KEY_ID="trexaccesskey"
    export AWS_SECRET_ACCESS_KEY="trex123321"
    export AWS_DEFAULT_REGION="us-east-1"
    export S3_SECURE="0"
    export WORKER_BROKER_URL="redis://0.0.0.0:6379/13"
    export WORKER_BACKEND_URL="redis://0.0.0.0:6379/14"

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import os
import datetime
import json
import analysis_engine.consts as ae_consts
import analysis_engine.algo as base_algo
import analysis_engine.utils as ae_utils
import analysis_engine.build_algo_request as algo_utils
import analysis_engine.build_dataset_node as build_ds_node
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def run_algo(
        ticker=None,
        tickers=None,
        algo=None,  # optional derived ``analysis_engine.algo.Algo`` instance
        balance=None,     # float starting base capital
        commission=None,  # float for single trade commission for buy or sell
        start_date=None,  # string YYYY-MM-DD HH:MM:SS
        end_date=None,    # string YYYY-MM-DD HH:MM:SS
        datasets=None,    # string list of identifiers
        num_owned_dict=None,  # not supported
        cache_freq='daily',   # 'minute' not supported
        auto_fill=True,
        load_config=None,
        report_config=None,
        history_config=None,
        extract_config=None,
        use_key=None,
        extract_mode='all',
        iex_datasets=None,
        redis_enabled=True,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        redis_key=None,
        s3_enabled=True,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=False,
        s3_key=None,
        celery_disabled=True,
        broker_url=None,
        result_backend=None,
        label=None,
        name=None,
        timeseries=None,
        trade_strategy=None,
        verbose=False,
        publish_to_slack=True,
        publish_to_s3=True,
        publish_to_redis=True,
        extract_datasets=None,
        config_file=None,
        config_dict=None,
        version=1,
        raise_on_err=True,
        **kwargs):
    """run_algo

    Run an algorithm with steps:

        1) Extract redis keys between dates
        2) Compile a data pipeline dictionary (call it ``data``)
        3) Call algorithm's ``myalgo.handle_data(data=data)``

    .. note:: If no ``algo`` is set, the
        ``analysis_engine.algo.BaseAlgo`` algorithm
        is used.

    .. note:: Please ensure Redis and Minio are running
        before trying to extract tickers

    **Stock tickers to extract**

    :param ticker: single stock ticker/symbol/ETF to extract
    :param tickers: optional - list of tickers to extract
    :param use_key: optional - extract historical key from Redis

    **Algo Configuration**

    :param algo: derived instance of ``analysis_engine.algo.Algo`` object
    :param balance: optional - float balance parameter
        can also be set on the ``algo`` object if not
        set on the args
    :param commission: float for single trade commission for
        buy or sell. can also be set on the ``algo`` objet
    :param start_date: string ``YYYY-MM-DD_HH:MM:SS`` cache value
    :param end_date: string ``YYYY-MM-DD_HH:MM:SS`` cache value
    :param dataset_types: list of strings that are ``iex`` or ``yahoo``
        datasets that are cached.
    :param cache_freq: optional - depending on if you are running data feeds
        on a ``daily`` cron (default) vs every ``minute`` (or faster)
    :param num_owned_dict: not supported yet
    :param auto_fill: optional - boolean for auto filling
        buy/sell orders for backtesting (default is
        ``True``)
    :param trading_calendar: ``trading_calendar.TradingCalendar``
        object, by default ``analysis_engine.calendars.
        always_open.AlwaysOpen`` trading calendar
        # TradingCalendar by ``TFSExchangeCalendar``
    :param config_file: path to a json file
        containing custom algorithm object
        member values (like indicator configuration and
        predict future date units ahead for a backtest)
    :param config_dict: optional - dictionary that
        can be passed to derived class implementations
        of: ``def load_from_config(config_dict=config_dict)``

    **Timeseries**

    :param timeseries: optional - string to
        set ``day`` or ``minute`` backtesting
        or live trading
        (default is ``minute``)

    **Trading Strategy**

    :param trade_strategy: optional - string to
        set the type of ``Trading Strategy``
        for backtesting or live trading
        (default is ``count``)

    **Algorithm Dataset Loading, Extracting, Reporting
    and Trading History arguments**

    :param load_config: optional - dictionary
        for setting member variables to load an
        agorithm-ready dataset from
        a file, s3 or redis
    :param report_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack
    :param history_config: optional - dictionary
        for setting member variables to publish
        an algo ``trade history`` to s3, redis, a file
        or slack
    :param extract_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack

    **(Optional) Data sources, datafeeds and datasets to gather**

    :param iex_datasets: list of strings for gathering specific `IEX
        datasets <https://iexcloud.io/>`__
        which are set as consts: ``analysis_engine.iex.consts.FETCH_*``.

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``True``)
    :param redis_address: Redis connection string
        format is ``host:port``
        (default is ``localhost:6379``)
    :param redis_db: Redis db to use
        (default is ``0``)
    :param redis_password: optional - Redis password
        (default is ``None``)
    :param redis_expire: optional - Redis expire value
        (default is ``None``)
    :param redis_key: optional - redis key not used
        (default is ``None``)

    **(Optional) Minio (S3) connectivity arguments**

    :param s3_enabled: bool - toggle for auto-archiving on Minio (S3)
        (default is ``True``)
    :param s3_address: Minio S3 connection string
        format ``host:port``
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
    :param s3_key: optional s3 key not used
        (default is ``None``)

    **(Optional) Celery worker broker connectivity arguments**

    :param celery_disabled: bool - toggle synchronous mode or publish
        to an engine connected to the `Celery broker and backend
        <https://github.com/celery/celery#transports-and-backends>`__
        (default is ``True`` - synchronous mode without an engine
        or need for a broker or backend for Celery)
    :param broker_url: Celery broker url
        (default is ``redis://0.0.0.0:6379/13``)
    :param result_backend: Celery backend url
        (default is ``redis://0.0.0.0:6379/14``)
    :param label: tracking log label
    :param publish_to_slack: optional - boolean for
        publishing to slack (coming soon)
    :param publish_to_s3: optional - boolean for
        publishing to s3 (coming soon)
    :param publish_to_redis: optional - boolean for
        publishing to redis (coming soon)

    **(Optional) Debugging**

    :param verbose: bool - show extract warnings
        and other debug logging (default is False)
    :param raise_on_err: optional - boolean for
        unittests and developing algorithms with the
        ``analysis_engine.run_algo.run_algo`` helper.
        When set to ``True`` exceptions will
        are raised to the calling functions

    :param kwargs: keyword arguments dictionary
    """

    # dictionary structure with a list sorted on: ascending dates
    # algo_data_req[ticker][list][dataset] = pd.DataFrame
    algo_data_req = {}
    extract_requests = []
    return_algo = False  # return created algo objects for use by caller
    rec = {}
    msg = None

    use_tickers = tickers
    use_balance = balance
    use_commission = commission

    if ticker:
        use_tickers = [ticker]
    else:
        if not use_tickers:
            use_tickers = []

    # if these are not set as args, but the algo object
    # has them, use them instead:
    if algo:
        if len(use_tickers) == 0:
            use_tickers = algo.get_tickers()
        if not use_balance:
            use_balance = algo.get_balance()
        if not use_commission:
            use_commission = algo.get_commission()

    default_iex_datasets = [
        'daily',
        'minute',
        'quote',
        'stats',
        'peers',
        'news',
        'financials',
        'earnings',
        'dividends',
        'company'
    ]

    if not iex_datasets:
        iex_datasets = default_iex_datasets

    if redis_enabled:
        if not redis_address:
            redis_address = os.getenv(
                'REDIS_ADDRESS',
                'localhost:6379')
        if not redis_password:
            redis_password = os.getenv(
                'REDIS_PASSWORD',
                None)
        if not redis_db:
            redis_db = int(os.getenv(
                'REDIS_DB',
                '0'))
        if not redis_expire:
            redis_expire = os.getenv(
                'REDIS_EXPIRE',
                None)
    if s3_enabled:
        if not s3_address:
            s3_address = os.getenv(
                'S3_ADDRESS',
                'localhost:9000')
        if not s3_access_key:
            s3_access_key = os.getenv(
                'AWS_ACCESS_KEY_ID',
                'trexaccesskey')
        if not s3_secret_key:
            s3_secret_key = os.getenv(
                'AWS_SECRET_ACCESS_KEY',
                'trex123321')
        if not s3_region_name:
            s3_region_name = os.getenv(
                'AWS_DEFAULT_REGION',
                'us-east-1')
        if not s3_secure:
            s3_secure = os.getenv(
                'S3_SECURE',
                '0') == '1'
        if not s3_bucket:
            s3_bucket = os.getenv(
                'S3_BUCKET',
                'dev')
    if not broker_url:
        broker_url = os.getenv(
            'WORKER_BROKER_URL',
            'redis://0.0.0.0:6379/11')
    if not result_backend:
        result_backend = os.getenv(
            'WORKER_BACKEND_URL',
            'redis://0.0.0.0:6379/12')

    if not label:
        label = 'run-algo'

    num_tickers = len(use_tickers)
    last_close_str = ae_utils.get_last_close_str()

    if iex_datasets:
        if verbose:
            log.info(
                f'{label} - tickers={num_tickers} '
                f'iex={json.dumps(iex_datasets)}')
    else:
        if verbose:
            log.info(f'{label} - tickers={num_tickers}')

    ticker_key = use_key
    if not ticker_key:
        ticker_key = f'{ticker}_{last_close_str}'

    if not algo:
        algo = base_algo.BaseAlgo(
            ticker=None,
            tickers=use_tickers,
            balance=use_balance,
            commission=use_commission,
            config_dict=config_dict,
            name=label,
            auto_fill=auto_fill,
            timeseries=timeseries,
            trade_strategy=trade_strategy,
            publish_to_slack=publish_to_slack,
            publish_to_s3=publish_to_s3,
            publish_to_redis=publish_to_redis,
            raise_on_err=raise_on_err)
        return_algo = True
        # the algo object is stored
        # in the result at: res['rec']['algo']

    if not algo:
        msg = f'{label} - missing algo object'
        log.error(msg)
        return build_result.build_result(
                status=ae_consts.EMPTY,
                err=msg,
                rec=rec)

    if raise_on_err:
        log.debug(f'{label} - enabling algo exception raises')
        algo.raise_on_err = True

    indicator_datasets = algo.get_indicator_datasets()
    if len(indicator_datasets) == 0:
        indicator_datasets = ae_consts.BACKUP_DATASETS
        log.info(
            f'using all datasets={indicator_datasets}')

    verbose_extract = False
    if config_dict:
        verbose_extract = config_dict.get('verbose_extract', False)

    common_vals = {}
    common_vals['base_key'] = ticker_key
    common_vals['celery_disabled'] = celery_disabled
    common_vals['ticker'] = ticker
    common_vals['label'] = label
    common_vals['iex_datasets'] = iex_datasets
    common_vals['s3_enabled'] = s3_enabled
    common_vals['s3_bucket'] = s3_bucket
    common_vals['s3_address'] = s3_address
    common_vals['s3_secure'] = s3_secure
    common_vals['s3_region_name'] = s3_region_name
    common_vals['s3_access_key'] = s3_access_key
    common_vals['s3_secret_key'] = s3_secret_key
    common_vals['s3_key'] = ticker_key
    common_vals['redis_enabled'] = redis_enabled
    common_vals['redis_address'] = redis_address
    common_vals['redis_password'] = redis_password
    common_vals['redis_db'] = redis_db
    common_vals['redis_key'] = ticker_key
    common_vals['redis_expire'] = redis_expire

    use_start_date_str = start_date
    use_end_date_str = end_date
    last_close_date = ae_utils.last_close()
    end_date_val = None

    cache_freq_fmt = ae_consts.COMMON_TICK_DATE_FORMAT

    if not use_end_date_str:
        use_end_date_str = last_close_date.strftime(
            cache_freq_fmt)

    end_date_val = ae_utils.get_date_from_str(
        date_str=use_end_date_str,
        fmt=cache_freq_fmt)
    start_date_val = None

    if not use_start_date_str:
        start_date_val = end_date_val - datetime.timedelta(
            days=60)
        use_start_date_str = start_date_val.strftime(
            cache_freq_fmt)
    else:
        start_date_val = datetime.datetime.strptime(
            use_start_date_str,
            ae_consts.COMMON_TICK_DATE_FORMAT)

    total_dates = (end_date_val - start_date_val).days

    if end_date_val < start_date_val:
        msg = (
            f'{label} - invalid dates - start_date={start_date_val} is after '
            f'end_date={end_date_val}')
        raise Exception(msg)

    if verbose:
        log.info(
            f'{label} - days={total_dates} '
            f'start={use_start_date_str} '
            f'end={use_end_date_str} '
            f'datasets={indicator_datasets}')

    for ticker in use_tickers:
        req = algo_utils.build_algo_request(
            ticker=ticker,
            use_key=use_key,
            start_date=use_start_date_str,
            end_date=use_end_date_str,
            datasets=datasets,
            balance=use_balance,
            cache_freq=cache_freq,
            timeseries=timeseries,
            trade_strategy=trade_strategy,
            label=label)
        ticker_key = f'{ticker}_{last_close_str}'
        common_vals['ticker'] = ticker
        common_vals['base_key'] = ticker_key
        common_vals['redis_key'] = ticker_key
        common_vals['s3_key'] = ticker_key

        for date_key in req['extract_datasets']:
            date_req = api_requests.get_ds_dict(
                ticker=ticker,
                base_key=date_key,
                ds_id=label,
                service_dict=common_vals)
            node_date_key = date_key.replace(
                f'{ticker}_',
                '')
            extract_requests.append({
                'id': date_key,
                'ticker': ticker,
                'date_key': date_key,
                'date': node_date_key,
                'req': date_req})
    # end of for all ticker in use_tickers

    first_extract_date = None
    last_extract_date = None
    total_extract_requests = len(extract_requests)
    cur_idx = 1
    for idx, extract_node in enumerate(extract_requests):

        extract_ticker = extract_node['ticker']
        extract_date = extract_node['date']
        ds_node_id = extract_node['id']

        if not first_extract_date:
            first_extract_date = extract_date
        last_extract_date = extract_date
        perc_progress = ae_consts.get_percent_done(
            progress=cur_idx,
            total=total_extract_requests)
        percent_label = (
            f'{label} '
            f'ticker={extract_ticker} '
            f'date={extract_date} '
            f'{perc_progress} '
            f'{idx}/{total_extract_requests} '
            f'{indicator_datasets}')
        if verbose:
            log.info(
                f'extracting - {percent_label}')

        ticker_bt_data = build_ds_node.build_dataset_node(
            ticker=extract_ticker,
            date=extract_date,
            service_dict=common_vals,
            datasets=indicator_datasets,
            log_label=label,
            verbose=verbose_extract)

        if ticker not in algo_data_req:
            algo_data_req[ticker] = []

        algo_data_req[ticker].append({
            'id': ds_node_id,  # id is currently the cache key in redis
            'date': extract_date,  # used to confirm dates in asc order
            'data': ticker_bt_data
        })

        if verbose:
            log.info(
                f'extract - {percent_label} '
                f'dataset={len(algo_data_req[ticker])}')
        cur_idx += 1
    # end of for service_dict in extract_requests

    # this could be a separate celery task
    status = ae_consts.NOT_RUN
    if len(algo_data_req) == 0:
        msg = (
            f'{label} - nothing to test - no data found for '
            f'tickers={use_tickers} '
            f'between {first_extract_date} and {last_extract_date}')
        log.info(msg)
        return build_result.build_result(
            status=ae_consts.EMPTY,
            err=msg,
            rec=rec)

    # this could be a separate celery task
    try:
        if verbose:
            log.info(
                f'handle_data START - {percent_label} from '
                f'{first_extract_date} to {last_extract_date}')
        algo.handle_data(
            data=algo_data_req)
        if verbose:
            log.info(
                f'handle_data END - {percent_label} from '
                f'{first_extract_date} to {last_extract_date}')
    except Exception as e:
        a_name = algo.get_name()
        a_debug_msg = algo.get_debug_msg()
        if not a_debug_msg:
            a_debug_msg = 'debug message not set'
        a_config_dict = ae_consts.ppj(algo.config_dict)
        msg = (
            f'{percent_label} - algo={a_name} '
            f'encountered exception in handle_data tickers={use_tickers} '
            f'from {first_extract_date} to {last_extract_date} ex={e} '
            f'and failed during operation: {a_debug_msg}')
        if raise_on_err:
            if algo:
                try:
                    ind_obj = \
                        algo.get_indicator_process_last_indicator()
                    if ind_obj:
                        ind_obj_path = ind_obj.get_path_to_module()
                        ind_obj_config = ae_consts.ppj(
                            ind_obj.get_config())
                        found_error_hint = False
                        if hasattr(ind_obj.use_df, 'to_json'):
                            if len(ind_obj.use_df.index) == 0:
                                log.critical(
                                    f'indicator failure report for '
                                    f'last module: '
                                    f'{ind_obj_path} '
                                    f'indicator={ind_obj.get_name()} '
                                    f'config={ind_obj_config} '
                                    f'dataset={ind_obj.use_df.head(5)} '
                                    f'name_of_dataset={ind_obj.uses_data}')
                                log.critical(
                                    f'--------------------------------------'
                                    f'--------------------------------------')
                                log.critical(
                                    f'Please check if this indicator: '
                                    f'{ind_obj_path} '
                                    f'supports Empty Dataframes')
                                log.critical(
                                    f'--------------------------------------'
                                    f'--------------------------------------')
                                found_error_hint = True
                        # indicator error hints

                        if not found_error_hint:
                            log.critical(
                                f'indicator failure report for last module: '
                                f'{ind_obj_path} '
                                f'indicator={ind_obj.get_name()} '
                                f'config={ind_obj_config} '
                                f'dataset={ind_obj.use_df.head(5)} '
                                f'name_of_dataset={ind_obj.uses_data}')
                except Exception as f:
                    log.critical(
                        f'failed to pull indicator processor '
                        f'last indicator for debugging '
                        f'from ex={e} with parsing ex={f}')
                # end of ignoring non-supported ways of creating
                # indicator processors
            log.error(msg)
            log.error(
                f'algo failure report: '
                f'algo={a_name} handle_data() '
                f'config={a_config_dict} ')
            log.critical(
                f'algo failed during operation: {a_debug_msg}')
            raise e
        else:
            log.error(msg)
            return build_result.build_result(
                status=ae_consts.ERR,
                err=msg,
                rec=rec)
    # end of try/ex

    # this could be a separate celery task
    try:
        if verbose:
            log.info(
                f'get_result START - {percent_label} from '
                f'{first_extract_date} to {last_extract_date}')
        rec = algo.get_result()
        status = ae_consts.SUCCESS
        if verbose:
            log.info(
                f'get_result END - {percent_label} from '
                f'{first_extract_date} to {last_extract_date}')
    except Exception as e:
        msg = (
            f'{percent_label} - algo={algo.get_name()} encountered exception '
            f'in get_result tickers={use_tickers} from '
            f'{first_extract_date} to {last_extract_date} ex={e}')
        if raise_on_err:
            if algo:
                log.error(
                    f'algo={algo.get_name()} failed in get_result with '
                    f'debug_msg={algo.get_debug_msg()}')
            log.error(msg)
            raise e
        else:
            log.error(msg)
            return build_result.build_result(
                status=ae_consts.ERR,
                err=msg,
                rec=rec)
    # end of try/ex

    if return_algo:
        rec['algo'] = algo

    return build_result.build_result(
        status=status,
        err=msg,
        rec=rec)
# end of run_algo
