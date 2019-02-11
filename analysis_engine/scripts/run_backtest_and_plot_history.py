#!/usr/bin/env python

"""
A tool for showing how to build an algorithm and
run a backtest with an algorithm config dictionary

.. code-block:: python

    import analysis_engine.consts as ae_consts
    import analysis_engine.algo as base_algo
    import analysis_engine.run_algo as run_algo

    ticker = 'SPY'

    willr_close_path = (
        'analysis_engine/mocks/example_indicator_williamsr.py')
    willr_open_path = (
        'analysis_engine/mocks/example_indicator_williamsr_open.py')
    algo_config_dict = {
        'name': 'min-runner',
        'timeseries': timeseries,
        'trade_horizon': 5,
        'num_owned': 10,
        'buy_shares': 10,
        'balance': 10000.0,
        'commission': 6.0,
        'ticker': ticker,
        'algo_module_path': None,
        'algo_version': 1,
        'verbose': False,               # log in the algorithm
        'verbose_processor': False,     # log in the indicator processor
        'verbose_indicators': False,    # log all indicators
        'verbose_trading': True,        # log in the algo trading methods
        'positions': {
            ticker: {
                'shares': 10,
                'buys': [],
                'sells': []
            }
        },
        'buy_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'sell_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'indicators': [
            {
                'name': 'willr_-70_-30',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 80,
                'buy_below': -70,
                'sell_above': -30,
                'is_buy': False,
                'is_sell': False,
                'verbose': False  # log in just this indicator
            },
            {
                'name': 'willr_-80_-20',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 30,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_-90_-10',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 60,
                'buy_below': -90,
                'sell_above': -10,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_open_-80_-20',
                'module_path': willr_open_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_open_value': 0,
                'num_points': 80,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            }
        ],
        'slack': {
            'webhook': None
        }
    }

    class ExampleCustomAlgo(base_algo.BaseAlgo):
        def process(self, algo_id, ticker, dataset):
            if self.verbose:
                print(
                    f'process start - {self.name} '
                    f'date={self.backtest_date} minute={self.latest_min} '
                    f'close={self.latest_close} high={self.latest_high} '
                    f'low={self.latest_low} open={self.latest_open} '
                    f'volume={self.latest_volume}')
        # end of process
    # end of ExampleCustomAlgo


    algo_obj = ExampleCustomAlgo(
        ticker=algo_config_dict['ticker'],
        config_dict=algo_config_dict)

    algo_res = run_algo.run_algo(
        ticker=algo_config_dict['ticker'],
        algo=algo_obj,
        raise_on_err=True)

    if algo_res['status'] != ae_consts.SUCCESS:
        print(
            'failed running algo backtest '
            f'{algo_obj.get_name()} hit status: '
            f'{ae_consts.get_status(status=algo_res['status'])} '
            f'error: {algo_res["err"]}')
    else:
        print(
            f'backtest: {algo_obj.get_name()} '
            f'{ae_consts.get_status(status=algo_res["status"])} - '
            'plotting history')
    # if not successful

"""

import os
import sys
import datetime
import argparse
import analysis_engine.consts as ae_consts
import analysis_engine.algo as base_algo
import analysis_engine.run_algo as run_algo
import analysis_engine.plot_trading_history as plot_trading_history
import analysis_engine.build_publish_request as build_publish_request
import spylunking.log.setup_logging as log_utils


log = log_utils.build_colorized_logger(
    name='bt',
    log_config_path=ae_consts.LOG_CONFIG_PATH)


def build_example_algo_config(
        ticker,
        timeseries='minute'):
    """build_example_algo_config

    helper for building an algorithm config dictionary

    :returns: algorithm config dictionary
    """
    willr_close_path = (
        'analysis_engine/mocks/example_indicator_williamsr.py')
    willr_open_path = (
        'analysis_engine/mocks/example_indicator_williamsr_open.py')
    algo_config_dict = {
        'name': 'backtest',
        'timeseries': timeseries,
        'trade_horizon': 5,
        'num_owned': 10,
        'buy_shares': 10,
        'balance': 10000.0,
        'commission': 6.0,
        'ticker': ticker,
        'algo_module_path': None,
        'algo_version': 1,
        'verbose': False,  # log in the algorithm
        'verbose_processor': False,  # log in the indicator processor
        'verbose_indicators': False,  # log all indicators
        'verbose_trading': False,  # log in the algo trading methods
        'inspect_datasets': False,  # log dataset metrics - slow
        'positions': {
            ticker: {
                'shares': 10,
                'buys': [],
                'sells': []
            }
        },
        'buy_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'sell_rules': {
            'confidence': 75,
            'min_indicators': 3
        },
        'indicators': [
            {
                'name': 'willr_-70_-30',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 80,
                'buy_below': -70,
                'sell_above': -30,
                'is_buy': False,
                'is_sell': False,
                'verbose': False  # log in just this indicator
            },
            {
                'name': 'willr_-80_-20',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 30,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_-90_-10',
                'module_path': willr_close_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_value': 0,
                'num_points': 60,
                'buy_below': -90,
                'sell_above': -10,
                'is_buy': False,
                'is_sell': False
            },
            {
                'name': 'willr_open_-80_-20',
                'module_path': willr_open_path,
                'category': 'technical',
                'type': 'momentum',
                'uses_data': 'minute',
                'high': 0,
                'low': 0,
                'close': 0,
                'open': 0,
                'willr_open_value': 0,
                'num_points': 80,
                'buy_below': -80,
                'sell_above': -20,
                'is_buy': False,
                'is_sell': False
            }
        ],
        'slack': {
            'webhook': None
        }
    }

    return algo_config_dict
# end of build_example_algo_config


class ExampleCustomAlgo(base_algo.BaseAlgo):
    """ExampleCustomAlgo"""

    def process(self, algo_id, ticker, dataset):
        """process

        Run a custom algorithm after all the indicators
        from the ``algo_config_dict`` have been processed and all
        the number crunching is done. This allows the algorithm
        class to focus on the high-level trade execution problems
        like bid-ask spreads and opening the buy/sell trade orders.

        **How does it work?**

        The engine provides a data stream from the latest
        pricing updates stored in redis. Once new data is
        stored in redis, algorithms will be able to use
        each ``dataset`` as a chance to evaluate buy and
        sell decisions. These are your own custom logic
        for trading based off what the indicators find
        and any non-indicator data provided from within
        the ``dataset`` dictionary.

        **Dataset Dictionary Structure**

        Here is what the ``dataset`` variable
        looks like when your algorithm's ``process``
        method is called (assuming you have redis running
        with actual pricing data too):

        .. code-block:: python

            dataset = {
                'id': dataset_id,
                'date': date,
                'data': {
                    'daily': pd.DataFrame([]),
                    'minute': pd.DataFrame([]),
                    'quote': pd.DataFrame([]),
                    'stats': pd.DataFrame([]),
                    'peers': pd.DataFrame([]),
                    'news1': pd.DataFrame([]),
                    'financials': pd.DataFrame([]),
                    'earnings': pd.DataFrame([]),
                    'dividends': pd.DataFrame([]),
                    'calls': pd.DataFrame([]),
                    'puts': pd.DataFrame([]),
                    'pricing': pd.DataFrame([]),
                    'news': pd.DataFrame([])
                }
            }

        .. tip:: you can also inspect these datasets by setting
            the algorithm's config dictionary key
            ``"inspect_datasets": True``

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
            multiple pandas ``DataFrame`` objects.
        """
        if self.verbose:
            log.info(
                f'process start - {self.name} balance={self.balance} '
                f'date={self.backtest_date} minute={self.latest_min} '
                f'close={self.latest_close} high={self.latest_high} '
                f'low={self.latest_low} open={self.latest_open} '
                f'volume={self.latest_volume}')
    # end of process

# end of ExampleCustomAlgo


def run_backtest_and_plot_history(
        config_dict):
    """run_backtest_and_plot_history

    Run a derived algorithm with an algorithm config dictionary

    :param config_dict: algorithm config dictionary
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
            'save the trading history dataframe '
            'to this file'),
        required=False,
        dest='history_json_file')
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
        '-c',
        help=(
            'optional - algorithm config_file path for setting '
            'up internal algorithm trading strategies and '
            'indicators'),
        required=False,
        dest='config_file')
    parser.add_argument(
        '-v',
        help=(
            'set the Algorithm to verbose logging'),
        required=False,
        dest='verbose_algo',
        action='store_true')
    parser.add_argument(
        '-P',
        help=(
            'set the Algorithm\'s IndicatorProcessor to verbose logging'),
        required=False,
        dest='verbose_processor',
        action='store_true')
    parser.add_argument(
        '-I',
        help=(
            'set all Algorithm\'s Indicators to verbose logging '
            '(note indivdual indicators support a \'verbose\' key '
            'that can be set to True to debug just one '
            'indicator)'),
        required=False,
        dest='verbose_indicators',
        action='store_true')
    parser.add_argument(
        '-V',
        help=(
            'inspect the datasets an algorithm is processing - this'
            'will slow down processing to show debugging'),
        required=False,
        dest='inspect_datasets',
        action='store_true')
    parser.add_argument(
        '-j',
        help=(
            'run the algorithm on just this specific date in the datasets '
            '- specify the date in a format: YYYY-MM-DD like: 2018-11-29'),
        required=False,
        dest='run_this_date')
    parser.add_argument(
        '-d',
        help=(
            'debug'),
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    ticker = ae_consts.TICKER
    use_balance = 10000.0
    use_commission = 6.0
    use_start_date = None
    use_end_date = None
    use_config_file = None
    debug = False
    verbose_algo = None
    verbose_processor = None
    verbose_indicators = None
    inspect_datasets = None
    history_json_file = None
    run_this_date = None

    s3_access_key = ae_consts.S3_ACCESS_KEY
    s3_secret_key = ae_consts.S3_SECRET_KEY
    s3_region_name = ae_consts.S3_REGION_NAME
    s3_address = ae_consts.S3_ADDRESS
    s3_secure = ae_consts.S3_SECURE
    redis_address = ae_consts.REDIS_ADDRESS
    redis_password = ae_consts.REDIS_PASSWORD
    redis_db = ae_consts.REDIS_DB
    redis_expire = ae_consts.REDIS_EXPIRE

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
    if args.redis_address:
        redis_address = args.redis_address
    if args.redis_db:
        redis_db = args.redis_db
    if args.redis_expire:
        redis_expire = args.redis_expire
    if args.history_json_file:
        history_json_file = args.history_json_file
    if args.ticker:
        ticker = args.ticker.upper()
    if args.debug:
        debug = True
    if args.verbose_algo:
        verbose_algo = True
    if args.verbose_processor:
        verbose_processor = True
    if args.verbose_indicators:
        verbose_indicators = True
    if args.inspect_datasets:
        inspect_datasets = True
    if args.run_this_date:
        run_this_date = args.run_this_date

    if args.start_date:
        try:
            use_start_date = f'{str(args.start_date)} 00:00:00'
            datetime.datetime.strptime(
                args.start_date,
                ae_consts.COMMON_DATE_FORMAT)
        except Exception as e:
            msg = (
                'please use a start date formatted as: '
                f'{ae_consts.COMMON_DATE_FORMAT}\nerror was: {e}')
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
                f'{ae_consts.COMMON_DATE_FORMAT}\nerror was: {e}')
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

        load_from_s3_bucket = None
        load_from_s3_key = None
        load_from_redis_key = None
        load_from_file = None

        if 's3://' in backtest_loc:
            load_from_s3_bucket = backtest_loc.split('/')[-2]
            load_from_s3_key = backtest_loc.split('/')[-1]
        elif 'redis://' in backtest_loc:
            load_from_redis_key = backtest_loc.split('/')[-1]
        elif 'file:/' in backtest_loc:
            load_from_file = backtest_loc.split(':')[-1]
        # end of parsing supported transport - loading an algo-ready

        load_config = build_publish_request.build_publish_request(
            ticker=ticker,
            output_file=load_from_file,
            s3_bucket=load_from_s3_bucket,
            s3_key=load_from_s3_key,
            redis_key=load_from_redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            s3_address=s3_address,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            verbose=debug,
            label=f'load-{backtest_loc}')
        if load_from_file:
            load_config['output_file'] = load_from_file
        if load_from_redis_key:
            load_config['redis_key'] = load_from_redis_key
            load_config['redis_enabled'] = True
        if load_from_s3_bucket and load_from_s3_key:
            load_config['s3_bucket'] = load_from_s3_bucket
            load_config['s3_key'] = load_from_s3_key
            load_config['s3_enabled'] = True

    if debug:
        log.info('starting algo')

    config_dict['ticker'] = ticker
    config_dict['balance'] = use_balance
    config_dict['commission'] = use_commission

    if verbose_algo:
        config_dict['verbose'] = verbose_algo
    if verbose_processor:
        config_dict['verbose_processor'] = verbose_processor
    if verbose_indicators:
        config_dict['verbose_indicators'] = verbose_indicators
    if inspect_datasets:
        config_dict['inspect_datasets'] = inspect_datasets
    if run_this_date:
        config_dict['run_this_date'] = run_this_date

    algo_obj = ExampleCustomAlgo(
        ticker=config_dict['ticker'],
        config_dict=config_dict)

    algo_res = run_algo.run_algo(
        ticker=ticker,
        algo=algo_obj,
        start_date=use_start_date,
        end_date=use_end_date,
        raise_on_err=True)

    if algo_res['status'] != ae_consts.SUCCESS:
        log.error(
            'failed running algo backtest '
            f'{algo_obj.get_name()} hit status: '
            f'{ae_consts.get_status(status=algo_res["status"])} '
            f'error: {algo_res["err"]}')
        return
    # if not successful

    log.info(
        f'backtest: {algo_obj.get_name()} '
        f'{ae_consts.get_status(status=algo_res["status"])}')

    trading_history_dict = algo_obj.get_history_dataset()
    history_df = trading_history_dict[ticker]
    if not hasattr(history_df, 'to_json'):
        return

    if history_json_file:
        log.info(f'saving history to: {history_json_file}')
        history_df.to_json(
            history_json_file,
            orient='records',
            date_format='iso')

    log.info('plotting history')

    use_xcol = 'date'
    use_as_date_format = '%d\n%b'
    xlabel = f'Dates vs {trading_history_dict["algo_name"]} values'
    ylabel = f'Algo {trading_history_dict["algo_name"]}\nvalues'
    df_filter = (history_df['close'] > 0.01)
    first_date = history_df[df_filter]['date'].iloc[0]
    end_date = history_df[df_filter]['date'].iloc[-1]
    if config_dict['timeseries'] == 'minute':
        use_xcol = 'minute'
        use_as_date_format = '%d %H:%M:%S\n%b'
        first_date = history_df[df_filter]['minute'].iloc[0]
        end_date = history_df[df_filter]['minute'].iloc[-1]
    title = (
        f'Trading History {ticker} for Algo '
        f'{trading_history_dict["algo_name"]}\n'
        f'Backtest dates from {first_date} to {end_date}')

    # set default hloc columns:
    blue = None
    green = None
    orange = None

    red = 'close'
    blue = 'balance'

    if debug:
        for i, r in history_df.iterrows():
            log.debug(f'{r["minute"]} - {r["close"]}')

    plot_trading_history.plot_trading_history(
        title=title,
        df=history_df,
        red=red,
        blue=blue,
        green=green,
        orange=orange,
        date_col=use_xcol,
        date_format=use_as_date_format,
        xlabel=xlabel,
        ylabel=ylabel,
        df_filter=df_filter,
        show_plot=True,
        dropna_for_all=True)

# end of run_backtest_and_plot_history


def start_backtest_with_plot_history():
    """start_backtest_with_plot_history

    setup.py helper for kicking off a backtest
    that will plot the trading history using
    seaborn and matplotlib showing
    the algorithm's balance vs the closing price
    of the asset
    """
    run_backtest_and_plot_history(
        config_dict=build_example_algo_config(
            ticker='SPY',
            timeseries='minute'))
# end of start_backtest_with_plot_history


if __name__ == '__main__':
    start_backtest_with_plot_history()
