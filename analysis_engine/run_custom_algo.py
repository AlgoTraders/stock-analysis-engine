"""
This is a wrapper for running your own custom algorithms

.. note:: Please refer to the `sa.py <https://
    github.com/AlgoTraders/stock-analysis-engine/blob/master/
    analysis_engine/scripts/sa.py>`__
    for the lastest usage examples.

Example with the command line tool:

::

    bt -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

"""

import os
import inspect
import types
import importlib.machinery
import datetime
import json
import analysis_engine.consts as ae_consts
import analysis_engine.build_algo_request as build_algo_request
import analysis_engine.build_publish_request as build_publish_request
import analysis_engine.build_result as build_result
import analysis_engine.run_algo as run_algo
import analysis_engine.work_tasks.get_celery_app as get_celery_app
import analysis_engine.algo as ae_algo
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def run_custom_algo(
        mod_path,
        ticker='SPY',
        balance=50000,
        commission=6.0,
        start_date=None,
        end_date=None,
        name='myalgo',
        auto_fill=True,
        config_file=None,
        config_dict=None,
        load_from_s3_bucket=None,
        load_from_s3_key=None,
        load_from_redis_key=None,
        load_from_file=None,
        load_compress=False,
        load_publish=True,
        load_config=None,
        report_redis_key=None,
        report_s3_bucket=None,
        report_s3_key=None,
        report_file=None,
        report_compress=False,
        report_publish=True,
        report_config=None,
        history_redis_key=None,
        history_s3_bucket=None,
        history_s3_key=None,
        history_file=None,
        history_compress=False,
        history_publish=True,
        history_config=None,
        extract_redis_key=None,
        extract_s3_bucket=None,
        extract_s3_key=None,
        extract_file=None,
        extract_save_dir=None,
        extract_compress=False,
        extract_publish=True,
        extract_config=None,
        publish_to_s3=True,
        publish_to_redis=True,
        publish_to_slack=True,
        dataset_type=ae_consts.SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,
        compress=False,
        encoding='utf-8',
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
        timeseries=None,
        trade_strategy=None,
        verbose=False,
        debug=False,
        dataset_publish_extract=False,
        dataset_publish_history=False,
        dataset_publish_report=False,
        run_on_engine=False,
        auth_url=ae_consts.WORKER_BROKER_URL,
        backend_url=ae_consts.WORKER_BACKEND_URL,
        include_tasks=ae_consts.INCLUDE_TASKS,
        ssl_options=ae_consts.SSL_OPTIONS,
        transport_options=ae_consts.TRANSPORT_OPTIONS,
        path_to_config_module=ae_consts.WORKER_CELERY_CONFIG_MODULE,
        raise_on_err=True):
    """run_custom_algo

    Run a custom algorithm that derives the
    ``analysis_engine.algo.BaseAlgo`` class

    .. note:: Make sure to only have **1**
        class defined in an algo module. Imports from
        other modules should work just fine.

    **Algorithm arguments**

    :param mod_path: file path to custom
        algorithm class module
    :param ticker: ticker symbol
    :param balance: float - starting balance capital
        for creating buys and sells
    :param commission: float - cost pet buy or sell
    :param name: string - name for tracking algorithm
        in the logs
    :param start_date: string - start date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param end_date: end date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param auto_fill: optional - boolean for auto filling
        buy and sell orders for backtesting
        (default is ``True``)
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

    **Running Distributed Algorithms on the Engine Workers**

    :param run_on_engine: optional - boolean
        flag for publishing custom algorithms
        to Celery ae workers for distributing
        algorithm workloads
        (default is ``False`` which will run algos locally)
        this is required for distributing algorithms
    :param auth_url: Celery broker address
        (default is ``redis://localhost:6379/11``
        or ``analysis_engine.consts.WORKER_BROKER_URL``
        environment variable)
        this is required for distributing algorithms
    :param backend_url: Celery backend address
        (default is ``redis://localhost:6379/12``
        or ``analysis_engine.consts.WORKER_BACKEND_URL``
        environment variable)
        this is required for distributing algorithms
    :param include_tasks: list of modules containing tasks to add
        (default is ``analysis_engine.consts.INCLUDE_TASKS``)
    :param ssl_options: security options dictionary
        (default is ``analysis_engine.consts.SSL_OPTIONS``)
    :param trasport_options: transport options dictionary
        (default is ``analysis_engine.consts.TRANSPORT_OPTIONS``)
    :param path_to_config_module: config module for advanced
        Celery worker connectivity requirements
        (default is ``analysis_engine.work_tasks.celery_config``
        or ``analysis_engine.consts.WORKER_CELERY_CONFIG_MODULE``)

    **Load Algorithm-Ready Dataset From Source**

    Use these arguments to load algorithm-ready datasets
    from supported sources (file, s3 or redis)

    :param load_from_s3_bucket: optional - string load the algo from an
        a previously-created s3 bucket holding an s3 key with an
        algorithm-ready dataset for use with:
        ``handle_data``
    :param load_from_s3_key: optional - string load the algo from an
        a previously-created s3 key holding an
        algorithm-ready dataset for use with:
        ``handle_data``
    :param load_from_redis_key: optional - string load the algo from a
        a previously-created redis key holding an
        algorithm-ready dataset for use with:
        ``handle_data``
    :param load_from_file: optional - string path to
        a previously-created local file holding an
        algorithm-ready dataset for use with:
        ``handle_data``
    :param load_compress: optional - boolean
        flag for toggling to decompress
        or not when loading an algorithm-ready
        dataset (``True`` means the dataset
        must be decompressed to load correctly inside
        an algorithm to run a backtest)
    :param load_publish: boolean - toggle publishing
        the load progress to slack, s3, redis or a file
        (default is ``True``)
    :param load_config: optional - dictionary
        for setting member variables to load an
        agorithm-ready dataset from
        a file, s3 or redis

    **Publishing Control Bool Flags**

    :param publish_to_s3: optional - boolean for
        toggling publishing to s3 on/off
        (default is ``True``)
    :param publish_to_redis: optional - boolean for
        publishing to redis on/off
        (default is ``True``)
    :param publish_to_slack: optional - boolean for
        publishing to slack
        (default is ``True``)

    **Algorithm Trade History Arguments**

    :param history_redis_key: optional - string
        where the algorithm trading history will be stored in
        an redis key
    :param history_s3_bucket: optional - string
        where the algorithm trading history will be stored in
        an s3 bucket
    :param history_s3_key: optional - string
        where the algorithm trading history will be stored in
        an s3 key
    :param history_file: optional - string key
        where the algorithm trading history will be stored in
        a file serialized as a json-string
    :param history_compress: optional - boolean
        flag for toggling to decompress
        or not when loading an algorithm-ready
        dataset (``True`` means the dataset
        will be compressed on publish)
    :param history_publish: boolean - toggle publishing
        the history to s3, redis or a file
        (default is ``True``)
    :param history_config: optional - dictionary
        for setting member variables to publish
        an algo ``trade history`` to s3, redis, a file
        or slack

    **Algorithm Trade Performance Report Arguments (Output Dataset)**

    :param report_redis_key: optional - string
        where the algorithm ``trading performance report`` (report)
        will be stored in an redis key
    :param report_s3_bucket: optional - string
        where the algorithm report will be stored in
        an s3 bucket
    :param report_s3_key: optional - string
        where the algorithm report will be stored in
        an s3 key
    :param report_file: optional - string key
        where the algorithm report will be stored in
        a file serialized as a json-string
    :param report_compress: optional - boolean
        flag for toggling to decompress
        or not when loading an algorithm-ready
        dataset (``True`` means the dataset
        will be compressed on publish)
    :param report_publish: boolean - toggle publishing
        the ``trading performance report`` s3, redis or a file
        (default is ``True``)
    :param report_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack

    **Extract an Algorithm-Ready Dataset Arguments**

    :param extract_redis_key: optional - string
        where the algorithm report will be stored in
        an redis key
    :param extract_s3_bucket: optional - string
        where the algorithm report will be stored in
        an s3 bucket
    :param extract_s3_key: optional - string
        where the algorithm report will be stored in
        an s3 key
    :param extract_file: optional - string key
        where the algorithm report will be stored in
        a file serialized as a json-string
    :param extract_save_dir: optional - string path to
        auto-generated files from the algo
    :param extract_compress: optional - boolean
        flag for toggling to decompress
        or not when loading an algorithm-ready
        dataset (``True`` means the dataset
        will be compressed on publish)
    :param extract_publish: boolean - toggle publishing
        the used ``algorithm-ready dataset`` to s3, redis or a file
        (default is ``True``)
    :param extract_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack

    **Dataset Arguments**

    :param dataset_type: optional - dataset type
        (default is ``SA_DATASET_TYPE_ALGO_READY``)
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
        (default is ``DEFAULT_SERIALIZED_DATASETS``)
    :param encoding: optional - string for data encoding

    **Publish Algorithm Datasets to S3, Redis or a File**

    :param dataset_publish_extract: optional - bool
        for publishing the algorithm's
        ``algorithm-ready``
        dataset to: s3, redis or file
    :param dataset_publish_history: optional - bool
        for publishing the algorithm's
        ``trading history``
        dataset to: s3, redis or file
    :param dataset_publish_report: optional - bool
        for publishing the algorithm's
        ``trading performance report``
        dataset to: s3, redis or file

    **Redis connectivity arguments**

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

    **Minio (S3) connectivity arguments**

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

    **Slack arguments**

    :param slack_enabled: optional - boolean for
        publishing to slack
    :param slack_code_block: optional - boolean for
        publishing as a code black in slack
    :param slack_full_width: optional - boolean for
        publishing as a to slack using the full
        width allowed

    **Debugging arguments**

    :param debug: optional - bool for debug tracking
    :param verbose: optional - bool for increasing
        logging
    :param raise_on_err: boolean - set this to ``False`` on prod
        to ensure exceptions do not interrupt services.
        With the default (``True``) any exceptions from the library
        and your own algorithm are sent back out immediately exiting
        the backtest.
    """

    module_name = 'BaseAlgo'
    custom_algo_module = None
    new_algo_object = None
    use_custom_algo = False
    found_algo_module = True
    should_publish_extract_dataset = False
    should_publish_history_dataset = False
    should_publish_report_dataset = False
    use_config_file = None
    use_config_dict = config_dict
    if config_file:
        if os.path.exists(config_file):
            use_config_file = config_file
            if not config_dict:
                try:
                    use_config_dict = json.loads(open(
                        config_file, 'r').read())
                except Exception as e:
                    msg = (
                        f'failed parsing json config_file={config_file} '
                        f'with ex={e}')
                    log.error(msg)
                    raise Exception(msg)
    # end of loading the config_file

    err = None
    if mod_path:
        module_name = mod_path.split('/')[-1]
        loader = importlib.machinery.SourceFileLoader(
            module_name,
            mod_path)
        custom_algo_module = types.ModuleType(
            loader.name)
        loader.exec_module(
            custom_algo_module)
        use_custom_algo = True

        for member in inspect.getmembers(custom_algo_module):
            if module_name in str(member):
                found_algo_module = True
                break
        # for all members in this custom module file
    # if loading a custom algorithm module from a file on disk

    if not found_algo_module:
        err = (
            f'unable to find custom algorithm module={custom_algo_module}')
        if mod_path:
            err = (
                'analysis_engine.run_custom_algo.run_custom_algo was unable '
                f'to find custom algorithm module={custom_algo_module} with '
                f'provided path to \n file: {mod_path} \n'
                '\n'
                'Please confirm '
                'that the class inherits from the BaseAlgo class like:\n'
                '\n'
                'import analysis_engine.algo\n'
                'class MyAlgo(analysis_engine.algo.BaseAlgo):\n '
                '\n'
                'If it is then please file an issue on github:\n '
                'https://github.com/AlgoTraders/stock-analysis-engine/'
                'issues/new \n\nFor now this error results in a shutdown'
                '\n')
        # if mod_path set

        if verbose or debug:
            log.error(err)
        return build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=None)
    # if not found_algo_module

    use_start_date = start_date
    use_end_date = end_date
    if not use_end_date:
        end_date = datetime.datetime.utcnow()
        use_end_date = end_date.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
    if not use_start_date:
        start_date = end_date - datetime.timedelta(days=75)
        use_start_date = start_date.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        if verbose:
            log.info(
                f'{name} {ticker} setting default start_date={use_start_date}')

    # Load an algorithm-ready dataset from:
    # file, s3, or redis
    if not load_config:
        load_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=None,
            s3_bucket=None,
            s3_key=None,
            redis_key=None,
            compress=load_compress,
            redis_enabled=publish_to_redis,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=publish_to_s3,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=publish_to_slack,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose,
            label=f'load-{name}')
        if load_from_file:
            load_config['output_file'] = load_from_file
        if load_from_redis_key:
            load_config['redis_key'] = load_from_redis_key
            load_config['redis_enabled'] = True
        if load_from_s3_bucket and load_from_s3_key:
            load_config['s3_bucket'] = load_from_s3_bucket
            load_config['s3_key'] = load_from_s3_key
            load_config['s3_enabled'] = True
    # end of building load_config dictionary if not already set

    # Automatically save all datasets to an algorithm-ready:
    # file, s3, or redis
    if not extract_config:
        extract_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=None,
            s3_bucket=None,
            s3_key=None,
            redis_key=None,
            compress=extract_compress,
            redis_enabled=publish_to_redis,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=publish_to_s3,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=publish_to_slack,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose,
            label=f'extract-{name}')
        should_publish_extract_dataset = False
        if extract_file:
            extract_config['output_file'] = extract_file
            should_publish_extract_dataset = True
        if extract_redis_key and publish_to_redis:
            extract_config['redis_key'] = extract_redis_key
            extract_config['redis_enabled'] = True
            should_publish_extract_dataset = True
        if extract_s3_bucket and extract_s3_key and publish_to_s3:
            extract_config['s3_bucket'] = extract_s3_bucket
            extract_config['s3_key'] = extract_s3_key
            extract_config['s3_enabled'] = True
            should_publish_extract_dataset = True
        else:
            extract_config['s3_enabled'] = False
    # end of building extract_config dictionary if not already set

    # Automatically save the trading performance report:
    # file, s3, or redis
    if not report_config:
        report_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=None,
            s3_bucket=None,
            s3_key=None,
            redis_key=None,
            compress=report_compress,
            redis_enabled=publish_to_redis,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=publish_to_s3,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=publish_to_slack,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose,
            label=f'report-{name}')
        should_publish_report_dataset = False
        if report_file:
            report_config['output_file'] = report_file
            should_publish_report_dataset = True
        if report_redis_key and publish_to_redis:
            report_config['redis_key'] = report_redis_key
            report_config['redis_enabled'] = True
            should_publish_report_dataset = True
        if report_s3_bucket and report_s3_key and publish_to_s3:
            report_config['s3_bucket'] = report_s3_bucket
            report_config['s3_key'] = report_s3_key
            report_config['s3_enabled'] = True
            should_publish_report_dataset = True
    # end of building report_config dictionary if not already set

    # Automatically save the trade history:
    # file, s3, or redis
    if not history_config:
        history_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=None,
            s3_bucket=None,
            s3_key=None,
            redis_key=None,
            compress=report_compress,
            redis_enabled=publish_to_redis,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            redis_encoding=redis_encoding,
            s3_enabled=publish_to_s3,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            slack_enabled=publish_to_slack,
            slack_code_block=slack_code_block,
            slack_full_width=slack_full_width,
            verbose=verbose,
            label=f'history-{name}')
        should_publish_history_dataset = False
        if history_file:
            history_config['output_file'] = history_file
            should_publish_history_dataset = True
        if history_redis_key and publish_to_redis:
            history_config['redis_key'] = history_redis_key
            history_config['redis_enabled'] = True
            should_publish_history_dataset = True
        if history_s3_bucket and history_s3_key and publish_to_s3:
            history_config['s3_bucket'] = history_s3_bucket
            history_config['s3_key'] = history_s3_key
            history_config['s3_enabled'] = True
            should_publish_history_dataset = True
    # end of building history_config dictionary if not already set

    if verbose:
        remove_vals = [
            's3_access_key',
            's3_secret_key',
            'redis_password'
        ]
        debug_extract_config = {}
        for k in extract_config:
            if k not in remove_vals:
                debug_extract_config[k] = extract_config[k]
        debug_report_config = {}
        for k in report_config:
            if k not in remove_vals:
                debug_report_config[k] = report_config[k]
        debug_history_config = {}
        for k in history_config:
            if k not in remove_vals:
                debug_history_config[k] = history_config[k]
        debug_load_config = {}
        for k in load_config:
            if k not in remove_vals:
                debug_load_config[k] = load_config[k]
        log.info(
            f'{name} {ticker} using extract config '
            f'{ae_consts.ppj(debug_extract_config)}')
        log.info(
            f'{name} {ticker} using report config '
            f'{ae_consts.ppj(debug_report_config)}')
        log.info(
            f'{name} {ticker} using trade history config '
            f'{ae_consts.ppj(debug_history_config)}')
        log.info(
            f'{name} {ticker} using load config '
            f'{ae_consts.ppj(debug_load_config)}')
        log.info(
            f'{name} {ticker} - building algo request')
    # end of verbose

    algo_req = build_algo_request.build_algo_request(
        ticker=ticker,
        balance=balance,
        commission=commission,
        start_date=use_start_date,
        end_date=use_end_date,
        timeseries=timeseries,
        trade_strategy=trade_strategy,
        config_file=use_config_file,
        config_dict=use_config_dict,
        load_config=load_config,
        history_config=history_config,
        report_config=report_config,
        extract_config=extract_config,
        label=name)

    algo_req['name'] = name
    algo_req['should_publish_extract_dataset'] = should_publish_extract_dataset
    algo_req['should_publish_history_dataset'] = should_publish_history_dataset
    algo_req['should_publish_report_dataset'] = should_publish_report_dataset

    algo_res = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=None)

    if run_on_engine:
        rec = {
            'algo_req': algo_req,
            'task_id': None
        }
        task_name = (
            'analysis_engine.work_tasks.'
            'task_run_algo.task_run_algo')
        if verbose:
            log.info(f'starting distributed algo task={task_name}')
        elif debug:
            log.info(
                'starting distributed algo by publishing to '
                f'task={task_name} broker={auth_url} backend={backend_url}')

        # Get the Celery app
        app = get_celery_app.get_celery_app(
            name=__name__,
            auth_url=auth_url,
            backend_url=backend_url,
            path_to_config_module=path_to_config_module,
            ssl_options=ssl_options,
            transport_options=transport_options,
            include_tasks=include_tasks)

        if debug:
            log.info(
                f'calling distributed algo task={task_name} '
                f'request={ae_consts.ppj(algo_req)}')
        elif verbose:
            log.info(f'calling distributed algo task={task_name}')

        job_id = app.send_task(
            task_name,
            (algo_req,))
        if verbose:
            log.info(f'calling task={task_name} - success job_id={job_id}')
        rec['task_id'] = job_id
        algo_res = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)
        return algo_res
    # end of run_on_engine

    if use_custom_algo:
        if verbose:
            log.info(
                f'inspecting {custom_algo_module} for class {module_name}')
        use_class_member_object = None
        for member in inspect.getmembers(custom_algo_module):
            if module_name in str(member):
                if verbose:
                    log.info(f'start {name} with {member[1]}')
                use_class_member_object = member
                break
        # end of looking over the class definition but did not find it

        if use_class_member_object:
            new_algo_object = member[1](
                **algo_req)
        else:
            err = (
                'did not find a derived analysis_engine.algo.BaseAlgo '
                f'class in the module file={mod_path} '
                f'for ticker={ticker} algo_name={name}')

            if verbose or debug:
                log.error(err)

            return build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=None)
        # end of finding a valid algorithm object
    else:
        new_algo_object = ae_algo.BaseAlgo(
            **algo_req)
    # if using a custom module path or the BaseAlgo

    if new_algo_object:
        # heads up - logging this might have passwords in the algo_req
        # log.debug(
        #     f'{name} algorithm request: {algo_req}')
        if verbose:
            log.info(
                f'{name} - run ticker={ticker} from {use_start_date} '
                f'to {use_end_date}')
        algo_res = run_algo.run_algo(
            algo=new_algo_object,
            raise_on_err=raise_on_err,
            **algo_req)
        algo_res['algo'] = new_algo_object
        if verbose:
            log.info(
                f'{name} - run ticker={ticker} from {use_start_date} '
                f'to {use_end_date}')
        if custom_algo_module:
            if verbose:
                log.info(
                    f'{name} - done run_algo '
                    f'custom_algo_module={custom_algo_module} '
                    f'module_name={module_name} ticker={ticker} '
                    f'from {use_start_date} to {use_end_date}')
        else:
            if verbose:
                log.info(
                    f'{name} - done run_algo BaseAlgo ticker={ticker} '
                    f'from {use_start_date} to {use_end_date}')
    else:
        err = (
            'missing a derived analysis_engine.algo.BaseAlgo '
            f'class in the module file={mod_path} for ticker={ticker} '
            f'algo_name={name}')
        return build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=None)
    # end of finding a valid algorithm object

    algo = algo_res.get(
        'algo',
        None)

    if not algo:
        err = (
            f'failed creating algorithm object - ticker={ticker} '
            f'status={ae_consts.get_status(status=algo_res["status"])} '
            f'error={algo_res["err"]} algo name={name} '
            f'custom_algo_module={custom_algo_module} '
            f'module_name={module_name} '
            f'from {use_start_date} to {use_end_date}')
        return build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=None)

    if should_publish_extract_dataset or dataset_publish_extract:
        s3_log = ''
        redis_log = ''
        file_log = ''
        use_log = 'publish'

        if (extract_config['redis_address'] and
                extract_config['redis_db'] >= 0 and
                extract_config['redis_key']):
            redis_log = (
                f'redis://{extract_config["redis_address"]}'
                f'@{extract_config["redis_db"]}/{extract_config["redis_key"]}')
            use_log += f' {redis_log}'
        else:
            extract_config['redis_enabled'] = False
        if (extract_config['s3_address'] and
                extract_config['s3_bucket'] and
                extract_config['s3_key']):
            s3_log = (
                f's3://{extract_config["s3_address"]}'
                f'/{extract_config["s3_bucket"]}/{extract_config["s3_key"]}')
            use_log += f' {s3_log}'
        else:
            extract_config['s3_enabled'] = False
        if extract_config['output_file']:
            file_log = f'file:{extract_config["output_file"]}'
            use_log += f' {file_log}'

        if verbose:
            log.info(
                f'{name} - publish - start ticker={ticker} '
                f'algorithm-ready {use_log}')

        publish_status = algo.publish_input_dataset(
            **extract_config)
        if publish_status != ae_consts.SUCCESS:
            msg = (
                'failed to publish algorithm-ready datasets '
                f'with status {ae_consts.get_status(status=publish_status)} '
                f'attempted to {use_log}')
            log.error(msg)
            return build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=None)

        if verbose:
            log.info(
                f'{name} - publish - done ticker={ticker} '
                f'algorithm-ready {use_log}')
    # if publish the algorithm-ready dataset

    if should_publish_history_dataset or dataset_publish_history:
        s3_log = ''
        redis_log = ''
        file_log = ''
        use_log = 'publish'

        if (history_config['redis_address'] and
                history_config['redis_db'] >= 0 and
                history_config['redis_key']):
            redis_log = (
                f'redis://{history_config["redis_address"]}'
                f'@{history_config["redis_db"]}/{history_config["redis_key"]}')
            use_log += f' {redis_log}'
        else:
            history_config['redis_enabled'] = False
        if (history_config['s3_address'] and
                history_config['s3_bucket'] and
                history_config['s3_key']):
            s3_log = (
                f's3://{history_config["s3_address"]}'
                f'/{history_config["s3_bucket"]}/{history_config["s3_key"]}')
            use_log += f' {s3_log}'
        else:
            history_config['s3_enabled'] = False

        if history_config['output_file']:
            file_log = f'file:{history_config["output_file"]}'
            use_log += f' {file_log}'

        if verbose:
            log.info(
                f'{name} - publish - start ticker={ticker} trading '
                f'history {use_log}')

        publish_status = algo.publish_trade_history_dataset(
            **history_config)
        if publish_status != ae_consts.SUCCESS:
            msg = (
                'failed to publish trading history datasets '
                f'with status {ae_consts.get_status(status=publish_status)} '
                f'attempted to {use_log}')
            log.error(msg)
            return build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=None)

        if verbose:
            log.info(
                f'{name} - publish - done ticker={ticker} trading '
                f'history {use_log}')
    # if publish an trading history dataset

    if should_publish_report_dataset or dataset_publish_report:
        s3_log = ''
        redis_log = ''
        file_log = ''
        use_log = 'publish'

        if (report_config['redis_address'] and
                report_config['redis_db'] >= 0 and
                report_config['redis_key']):
            redis_log = (
                f'redis://{report_config["redis_address"]}'
                f'@{report_config["redis_db"]}/{report_config["redis_key"]}')
            use_log += f' {redis_log}'
        else:
            report_config['redis_enabled'] = False
        if (report_config['s3_address'] and
                report_config['s3_bucket'] and
                report_config['s3_key']):
            s3_log = (
                f's3://{report_config["s3_address"]}'
                f'/{report_config["s3_bucket"]}/{report_config["s3_key"]}')
            use_log += f' {s3_log}'
        else:
            report_config['s3_enabled'] = False
        if report_config['output_file']:
            file_log = f'file:{report_config["output_file"]}'
            use_log += f' {file_log}'

        if verbose:
            log.info(
                f'{name} - publishing ticker={ticker} trading performance '
                f'report {use_log}')

        publish_status = algo.publish_report_dataset(
            **report_config)
        if publish_status != ae_consts.SUCCESS:
            msg = (
                'failed to publish trading performance report datasets '
                f'with status {ae_consts.get_status(status=publish_status)} '
                f'attempted to {use_log}')
            log.error(msg)
            return build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=None)

        if verbose:
            log.info(
                f'{name} - publish - done ticker={ticker} trading performance '
                f'report {use_log}')
    # if publish an trading performance report dataset

    if verbose:
        log.info(
            f'{name} - done publishing datasets for ticker={ticker} '
            f'from {use_start_date} to {use_end_date}')

    return algo_res
# end of run_custom_algo
