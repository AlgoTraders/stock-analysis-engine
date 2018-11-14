"""
This is a wrapper for running your own custom algorithms

.. note:: Please refer to the `sa.py <https://github.com/Algo
    Traders/stock-analysis-engine/blob/master/analysi
    s_engine/scripts/sa.py>`__ for the lastest usage examples.

Example with the command line tool:

::

    sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

"""

import inspect
import types
import importlib.machinery
import datetime
import analysis_engine.build_algo_request as build_algo_request
import analysis_engine.build_publish_request as build_publish_request
import analysis_engine.build_result as build_result
import analysis_engine.run_algo as run_algo
import analysis_engine.consts as sa_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def run_custom_algo(
        mod_path,
        ticker='SPY',
        balance=50000,
        commission=6.0,
        start_date=None,
        end_date=None,
        config_file=None,
        name='myalgo',
        auto_fill=True,
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
        publish_to_slack=False,
        publish_to_s3=False,
        publish_to_redis=False,
        dataset_type=sa_consts.SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=sa_consts.DEFAULT_SERIALIZED_DATASETS,
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
        verbose=False,
        debug=False,
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
    :param config_dict: optional - dictionary that
        can be passed to derived class implementations
        of: ``def load_from_config(config_dict=config_dict)``
    :param start_date: string - start date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param end_date: end date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param auto_fill: optional - boolean for auto filling
        buy and sell orders for backtesting
        (default is ``True``)
    :param config_file: path to a json file
        containing custom algorithm object
        member values

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
        (default is ``False``)
    :param publish_to_redis: optional - boolean for
        publishing to redis on/off
        (default is ``False``)
    :param publish_report: boolean - toggle publishing
        any generated datasets to s3 and redis
        (default ``True``)
    :param publish_to_slack: optional - boolean for
        publishing to slack
        (default is ``False``)

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
    module_name = mod_path.split('/')[-1]
    loader = importlib.machinery.SourceFileLoader(
        module_name, mod_path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)

    use_start_date = start_date
    use_end_date = end_date
    if not use_end_date:
        end_date = datetime.datetime.utcnow()
        use_end_date = end_date.strftime(
            sa_consts.COMMON_TICK_DATE_FORMAT)
    if not use_start_date:
        start_date = end_date - datetime.timedelta(days=75)
        use_start_date = start_date.strftime(
            sa_consts.COMMON_TICK_DATE_FORMAT)

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
            label='load-{}'.format(name))
        if load_from_file:
            load_config['output_file'] = load_from_file
        if load_from_redis_key:
            load_config['redis_key'] = load_from_redis_key
        if load_from_s3_bucket and load_from_s3_key:
            load_config['s3_bucket'] = load_from_s3_bucket
            load_config['s3_key'] = load_from_s3_key
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
            label='extract-{}'.format(name))
        if extract_file:
            extract_config['output_file'] = extract_file
        if extract_redis_key and publish_to_redis:
            extract_config['redis_key'] = extract_redis_key
        if extract_s3_bucket and extract_s3_key and publish_to_s3:
            extract_config['s3_bucket'] = extract_s3_bucket
            extract_config['s3_key'] = extract_s3_key
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
            label='report-{}'.format(name))
        if report_file:
            report_config['output_file'] = report_file
        if report_redis_key and publish_to_redis:
            report_config['redis_key'] = report_redis_key
        if report_s3_bucket and report_s3_key and publish_to_s3:
            report_config['s3_bucket'] = report_s3_bucket
            report_config['s3_key'] = report_s3_key
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
            label='history-{}'.format(name))
        if history_file:
            history_config['output_file'] = history_file
        if history_redis_key and publish_to_redis:
            history_config['redis_key'] = history_redis_key
        if history_s3_bucket and history_s3_key and publish_to_s3:
            history_config['s3_bucket'] = history_s3_bucket
            history_config['s3_key'] = history_s3_key
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
        log.info(
            '{} {} using extract config {}'.format(
                name,
                ticker,
                sa_consts.ppj(debug_extract_config)))
        log.info(
            '{} {} using report config {}'.format(
                name,
                ticker,
                sa_consts.ppj(debug_report_config)))
        log.info(
            '{} {} using trade history config {}'.format(
                name,
                ticker,
                sa_consts.ppj(debug_history_config)))
        log.info(
            '{} {} - building algo request'.format(
                name,
                ticker))
    # end of verbose

    algo_req = build_algo_request.build_algo_request(
        ticker=ticker,
        balance=balance,
        commission=commission,
        start_date=use_start_date,
        end_date=use_end_date,
        load_config=load_config,
        history_config=history_config,
        report_config=report_config,
        extract_config=extract_config,
        label=name)
    for member in inspect.getmembers(mod):
        if module_name in str(member):
            log.info(
                'start {} with {}'.format(
                    name,
                    member[1]))
            # heads up - logging this might have passwords in the algo_req
            # log.debug(
            #     '{} algorithm request: {}'.format(
            #         name,
            #         algo_req))
            algo_req['name'] = name
            custom_algo = member[1](
                **algo_req)
            log.debug(
                '{} run'.format(
                    name))
            algo_res = run_algo.run_algo(
                algo=custom_algo,
                raise_on_err=raise_on_err,
                **algo_req)
            algo_res['algo'] = custom_algo
            log.info(
                'done algorithm: {} with name={} '
                'from file={}'.format(
                    module_name,
                    name,
                    mod_path))
            return algo_res
    # end of looking over the class definition but did not find it

    log.error(
        'missing a derive analysis_engine.algo.BaseAlgo '
        'class in the module file={} for ticker={} algo_name={}'.format(
            mod_path,
            ticker,
            name))

    return build_result.build_result(
        status=sa_consts.ERR,
        rec=None)
# end of run_custom_algo
