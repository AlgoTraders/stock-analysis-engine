"""
Algorithms automatically provide the following
member variables to any custom algorithm that derives
the ``analysis_engine.algo.BaseAlgo.process`` method.

By deriving the ``process()`` member method using an inherited
class, you can quickly build algorithms that
determine **buy** and **sell** conditions from
any of the automatically extracted
datasets from the redis pipeline:

- ``self.df_daily``
- ``self.df_minute``
- ``self.df_calls``
- ``self.df_puts``
- ``self.df_quote``
- ``self.df_pricing``
- ``self.df_stats``
- ``self.df_peers``
- ``self.df_iex_news``
- ``self.df_financials``
- ``self.df_earnings``
- ``self.df_dividends``
- ``self.df_company``
- ``self.df_yahoo_news``

**Recent Pricing Information**

- ``self.latest_close``
- ``self.latest_high``
- ``self.latest_open``
- ``self.latest_low``
- ``self.latest_volume``
- ``self.today_close``
- ``self.today_high``
- ``self.today_open``
- ``self.today_low``
- ``self.today_volume``
- ``self.ask``
- ``self.bid``

**Latest Backtest Date and Intraday Minute**

- ``self.latest_min``
- ``self.backtest_date``

.. note:: **self.latest_min** - Latest minute row in ``self.df_minute``

.. note:: **self.backtest_date** - Latest dataset date which is considered the
    backtest date for historical testing with the data pipeline
    structure (it's the ``date`` key in the dataset node root level)

**Trading Strategy**

- ``self.trade_strategy = 'count'`` - if the number of indicators
    saying buy or sell exceeds the buy/sell rules ``min_indicators``
    the algorithm will trigger a buy or sell
- ``self.buy_reason`` - derived algorithms can attach custom
    buy reasons as a string to each trade order
- ``self.sell_reason`` - derived algorithms can attach custom
    sell reasons as a string to each trade order

**Timeseries**

- ``self.timeseries``- use an algorithm config to set
    ``day`` or ``minute`` to process daily or intraday
    minute by minute datasets. Indicators will still
    have access to all datasets, this just makes it
    easier to utilize the helper within an indicator
    to quickly get the correct dataset:

    .. code-block:: python

        df_status, use_df = self.get_subscribed_dataset(
            dataset=dataset)

**Balance Information**

- ``self.balance`` - current algorithm account balance
- ``self.prev_bal`` - previous balance
- ``self.net_value`` - total value the algorithm has
    left remaining since starting trading. this includes
    the number of ``self.num_owned`` shares with the
    ``self.latest_close`` price included
- ``self.net_gain`` - amount the algorithm has
    made since starting including owned shares
    with the ``self.latest_close`` price included

.. note:: If a key is not in the dataset, the
    algorithms's member variable will be an empty
    pandas DataFrame created with: ``pandas.DataFrame([])``
    except ``self.pricing`` which is just a dictionary.
    Please ensure the engine successfully fetched
    and cached the dataset in redis using a tool like
    ``redis-cli`` and a query of ``keys *`` or
    ``keys <TICKER>_*`` on large deployments.

**Indicator Information**

- ``self.buy_rules`` - optional - custom dictionary for passing
    buy-side business rules to a custom algorithm
- ``self.sell_rules`` - optional - custom dictionary for passing
    sale-side business rules to a custom algorithm
- ``self.min_buy_indicators`` - if ``self.buy_rules`` has
    a value for buying if a ``minimum`` number of indicators
    detect a value that is within a buy condition
- ``self.min_sell_indicators`` - if ``self.sell_rules`` has
    a value for selling if a ``minimum`` number of indicators
    detect a value that is within a sell condition
- ``self.latest_ind_report`` - latest dictionary of values
    from the ``IndicatorProcessor.process()``
- ``self.latest_buys`` - latest indicators saying buy
- ``self.latest_sells`` - latest indicators saying sell
- ``self.num_latest_buys`` - latest number of indicators saying buy
- ``self.num_latest_sells`` - latest number of indicators saying sell
- ``self.iproc`` - member variables for the ``IndicatorProcessor``
    that holds all of the custom algorithm indicators

Indicator buy and sell records in ``self.latest_buys`` and
``self.latest_sells`` have a dictionary structure:

.. code-block:: python

    {
        'name': indicator_name,
        'id': indicator_id,
        'report': indicator_report_dict,
        'cell': indicator cell number
    }

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import os
import json
import copy
import datetime
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.indicators.indicator_processor as ind_processor
import analysis_engine.build_trade_history_entry as history_utils
import analysis_engine.plot_trading_history as plot_trading_history
import analysis_engine.build_buy_order as buy_utils
import analysis_engine.build_sell_order as sell_utils
import analysis_engine.publish as publish
import analysis_engine.build_publish_request as build_publish_request
import analysis_engine.load_dataset as load_dataset
import analysis_engine.prepare_history_dataset as prepare_history
import analysis_engine.prepare_report_dataset as prepare_report
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class BaseAlgo:
    """BaseAlgo

    Run an algorithm against multiple tickers at once through the
    redis dataframe pipeline provided by
    `analysis_engine.extract.extract
    <https://github.com/AlgoTraders/stock-analysis-engine/bl
    ob/master/analysis_engine/extract.py>`__.

    **Data Pipeline Structure**

    This algorithm can handle an extracted dictionary with structure:

    .. code-block:: python

        import pandas as pd
        from analysis_engine.algo import BaseAlgo
        ticker = 'SPY'
        demo_algo = BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
            name='test-{}'.format(ticker))
        date = '2018-11-05'
        dataset_id = '{}_{}'.format(
            ticker,
            date)
        # mock the data pipeline in redis:
        data = {
            ticker: [
                {
                    'id': dataset_id,
                    'date': date,
                    'data': {
                        'daily': pd.DataFrame([
                            {
                                'high': 280.01,
                                'low': 270.01,
                                'open': 275.01,
                                'close': 272.02,
                                'volume': 123,
                                'date': '2018-11-01 15:59:59'
                            },
                            {
                                'high': 281.01,
                                'low': 271.01,
                                'open': 276.01,
                                'close': 273.02,
                                'volume': 124,
                                'date': '2018-11-02 15:59:59'
                            },
                            {
                                'high': 282.01,
                                'low': 272.01,
                                'open': 277.01,
                                'close': 274.02,
                                'volume': 121,
                                'date': '2018-11-05 15:59:59'
                            }
                        ]),
                        'calls': pd.DataFrame([]),
                        'puts': pd.DataFrame([]),
                        'minute': pd.DataFrame([]),
                        'pricing': pd.DataFrame([]),
                        'quote': pd.DataFrame([]),
                        'news': pd.DataFrame([]),
                        'news1': pd.DataFrame([]),
                        'dividends': pd.DataFrame([]),
                        'earnings': pd.DataFrame([]),
                        'financials': pd.DataFrame([]),
                        'stats': pd.DataFrame([]),
                        'peers': pd.DataFrame([]),
                        'company': pd.DataFrame([])
                    }
                }
            ]
        }

        # run the algorithm
        demo_algo.handle_data(data=data)

        # get the algorithm results
        results = demo_algo.get_result()

        print(results)
    """

    def __init__(
            self,
            ticker=None,
            balance=5000.0,
            commission=6.0,
            tickers=None,
            name=None,
            use_key=None,
            auto_fill=True,
            version=1,
            config_file=None,
            config_dict=None,
            output_dir=None,
            publish_to_slack=False,
            publish_to_s3=False,
            publish_to_redis=False,
            publish_input=True,
            publish_history=True,
            publish_report=True,
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
            dataset_type=ae_consts.SA_DATASET_TYPE_ALGO_READY,
            serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,
            timeseries=None,
            trade_strategy=None,
            verbose=False,
            verbose_processor=False,
            verbose_indicators=False,
            verbose_trading=False,
            inspect_datasets=False,
            raise_on_err=True,
            **kwargs):
        """__init__

        Build an analysis algorithm

        Use an algorithm object to:

        1) `Generate algorithm-ready datasets <https://gith
        ub.com/AlgoTraders/stock-analysis-engine#extra
        ct-algorithm-ready-datasets>`__
        2) Backtest trading theories with offline
        3) Issue trading alerts from the latest fetched datasets

        **(Optional) Trading Parameters**

        :param ticker: single ticker string
        :param balance: starting capital balance
            (default is ``5000.00``)
        :param commission: cost for commission
            for a single buy or sell trade
        :param tickers: optional - list of ticker strings
        :param name: optional - log tracking name
            or algo name
        :param use_key: optional - key for saving output
            in s3, redis, file
        :param auto_fill: optional - boolean for auto filling
            buy and sell orders for backtesting (default is
            ``True``)
        :param version: optional - version tracking
            value (default is ``1``)

        **Derived Config Loading for Indicators and Custom Backtest Values**

        :param config_file: path to a json file
            containing custom algorithm object
            member values (like indicator configuration and
            predict future date units ahead for a backtest)
        :param config_dict: optional - dictionary that
            can be passed to derived class implementations
            of: ``def load_from_config(config_dict=config_dict)``

        **Run a Backtest with an Algorithm-Ready Dataset in S3,
        Redis or a File**

        Use these arguments to load algorithm-ready datasets
        from supported sources (s3, redis or a file)

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
            for setting member variables to load
            an algorithm-ready dataset for backtesting
            (used by ``run_custom_algo``)

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
        :param history_file: optional - string file path for saving
            the ``trading history``
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
            an algo ``trade history``
            to s3, redis, a file or slack
            (used by ``run_custom_algo``)

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
        :param report_file: optional - string file path for saving
            the ``trading performance report``
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
            an algo ``result`` or
            ``trading performance report``
            to s3, redis, a file or slack
            (used by ``run_custom_algo``)

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
        :param extract_file: optional - string file path for saving
            the processed datasets as an``algorithm-ready`` dataset
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
            an algo ``input`` dataset (the contents of ``data``
            from ``self.handle_data(data=data)``
            (used by ``run_custom_algo``)

        **Dataset Arguments**

        :param dataset_type: optional - dataset type
            (default is ``ae_consts.SA_DATASET_TYPE_ALGO_READY``)
        :param serialize_datasets: optional - list of dataset names to
            deserialize in the dataset
            (default is ``ae_consts.DEFAULT_SERIALIZED_DATASETS``)
        :param encoding: optional - string for data encoding

        **(Optional) Publishing arguments**

        :param publish_to_slack: optional - boolean for
            publishing to slack (default is ``False``)
        :param publish_to_s3: optional - boolean for
            publishing to s3 (default is ``False``)
        :param publish_to_redis: optional - boolean for
            publishing to redis (default is ``False``)
        :param publish_input: boolean - toggle publishing
            all input datasets to s3 and redis
            (default ``True``)
        :param publish_history: boolean - toggle publishing
            the history to s3 and redis
            (default ``True``)
        :param publish_report: boolean - toggle publishing
            any generated datasets to s3 and redis
            (default ``True``)

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

        **Debugging arguments**

        :param verbose: optional - boolean for
            showing verbose algorithm logs
            (default is ``False``)
        :param verbose_processor: optional - boolean for
            showing verbose ``IndicatorProcessor`` logs
            (default is ``False``)
        :param verbose_indicators: optional - boolean for
            showing verbose ``Indicator`` logs
            (default is ``False`` which means an ``Indicator``
            can set ``'verbose': True`` to enable
            logging per individal ``Indicator``)
        :param verbose_trading: optional - boolean for logging
            in the trading functions including the reasons
            why a buy or sell was opened
        :param inspect_datasets: optional - boolean for logging
            what is sent to the algorithm's ``process()`` function
            (default is ``False`` as this will slow processing down)
        :param raise_on_err: optional - boolean for
            unittests and developing algorithms with the
            ``analysis_engine.run_algo.run_algo`` helper.
            .. note:: When set to ``True`` exceptions will
                are raised to the calling functions
        :param output_dir: optional - string path to
            auto-generated files from the algo

        **Future Argument Placeholder**

        :param kwargs: optional - dictionary of keyword
            arguments
        """
        self.buys = []
        self.sells = []
        self.num_shares = 0
        self.tickers = tickers
        if not self.tickers:
            if ticker:
                self.tickers = [
                    ticker.upper()
                ]
            else:
                raise Exception('BaseAlgo - please set a ticker to use')
        self.balance = balance
        self.starting_balance = balance
        self.starting_close = 0.0
        self.timeseries = timeseries
        if not self.timeseries:
            self.timeseries = 'minute'
        self.trade_strategy = trade_strategy
        if not self.trade_strategy:
            self.trade_strategy = 'count'
        self.timeseries_value = ae_consts.ALGO_TIMESERIES_MINUTE
        self.trade_horizon = 5
        self.commission = commission
        self.result = None
        self.name = name
        self.num_owned = None
        self.num_buys = 0
        self.num_sells = 0
        self.ticker_buys = []
        self.ticker_sell = []
        self.trade_price = 0.0
        self.today_high = 0.0
        self.today_low = 0.0
        self.today_open = 0.0
        self.today_close = 0.0
        self.today_volume = 0
        self.latest_close = 0.0
        self.latest_high = 0.0
        self.latest_open = 0.0
        self.latest_low = 0.0
        self.latest_volume = 0
        self.latest_min = None
        self.backtest_date = None
        self.ask = 0.0
        self.bid = 0.0
        self.prev_bal = None
        self.prev_num_owned = None
        self.ds_id = None
        self.trade_date = None
        self.trade_type = ae_consts.TRADE_SHARES
        self.buy_hold_units = 20
        self.sell_hold_units = 20
        self.spread_exp_date = None
        self.last_close = None
        self.order_history = []
        self.config_file = config_file
        self.config_dict = config_dict
        self.positions = {}
        self.created_on_date = datetime.datetime.utcnow()
        self.created_date = self.created_on_date.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
        self.created_buy = False
        self.should_buy = False
        self.buy_strength = None
        self.buy_risk = None
        self.created_sell = False
        self.should_sell = False
        self.sell_strength = None
        self.sell_risk = None
        self.stop_loss = None
        self.trailing_stop_loss = None

        self.last_handle_data = None
        self.last_ds_id = None
        self.last_ds_date = None
        self.last_ds_data = None

        self.ds_date = None
        self.ds_data = None
        self.df_daily = pd.DataFrame([{}])
        self.df_minute = pd.DataFrame([{}])
        self.df_stats = pd.DataFrame([{}])
        self.df_peers = pd.DataFrame([{}])
        self.df_financials = pd.DataFrame([])
        self.df_earnings = pd.DataFrame([{}])
        self.df_dividends = pd.DataFrame([{}])
        self.df_quote = pd.DataFrame([{}])
        self.df_company = pd.DataFrame([{}])
        self.df_iex_news = pd.DataFrame([{}])
        self.df_yahoo_news = pd.DataFrame([{}])
        self.df_calls = pd.DataFrame([{}])
        self.df_puts = pd.DataFrame([{}])
        self.df_pricing = pd.DataFrame([{}])
        self.empty_pd = pd.DataFrame([{}])
        self.empty_pd_str = ae_consts.EMPTY_DF_STR

        self.note = None
        self.debug_msg = ''
        self.version = version
        self.verbose = verbose
        self.verbose_processor = verbose_processor
        self.verbose_indicators = verbose_indicators
        self.verbose_trading = verbose_trading
        self.inspect_datasets = inspect_datasets
        self.run_this_date = None

        self.verbose = ae_consts.ev(
            'AE_DEBUG',
            '1') == '1'

        self.publish_to_slack = publish_to_slack
        self.publish_to_s3 = publish_to_s3
        self.publish_to_redis = publish_to_redis
        self.publish_history = publish_history
        self.publish_report = publish_report
        self.publish_input = publish_input
        self.raise_on_err = raise_on_err

        if not self.publish_to_s3:
            self.publish_to_s3 = ae_consts.ENABLED_S3_UPLOAD
        if not self.publish_to_redis:
            self.publish_to_redis = ae_consts.ENABLED_REDIS_PUBLISH

        self.output_file_dir = None
        self.output_file_prefix = None

        if self.raise_on_err:
            if self.tickers and len(self.tickers):
                self.output_file_prefix = str(
                    self.tickers[0]).upper()
            self.output_file_dir = '/opt/sa/tests/datasets/algo'

        if not self.name:
            self.name = 'myalgo'

        """
        Load tracking connectivity for recording
        - input
        - trade history
        - algorithm-generated datasets
        """

        # parse optional input args
        self.save_as_key = use_key
        if not self.save_as_key:
            self.save_as_key = '{}-{}'.format(
                self.name.replace(' ', ''),
                ae_utils.utc_now_str(fmt='%Y-%m-%d-%H-%M-%S.%f'))
        self.output_file_dir = '/opt/sa/tests/datasets/algo'
        if not output_dir:
            self.output_file_dir = output_dir

        # set up default keys
        self.default_output_file = '{}/{}.json'.format(
            self.output_file_dir,
            self.save_as_key)
        self.default_s3_key = '{}.json'.format(
            self.save_as_key)
        self.default_redis_key = '{}'.format(
            self.save_as_key)

        self.default_load_output_file = '{}/ready-{}.json'.format(
            self.output_file_dir,
            self.save_as_key)
        self.default_history_output_file = '{}/history-{}.json'.format(
            self.output_file_dir,
            self.save_as_key)
        self.default_report_output_file = '{}/report-{}.json'.format(
            self.output_file_dir,
            self.save_as_key)
        self.default_extract_output_file = '{}/extract-{}.json'.format(
            self.output_file_dir,
            self.save_as_key)

        self.default_load_redis_key = 'algo:ready:{}'.format(
            self.default_redis_key)
        self.default_history_redis_key = 'algo:history:{}'.format(
            self.default_redis_key)
        self.default_report_redis_key = 'algo:output:{}'.format(
            self.default_redis_key)
        self.default_extract_redis_key = 'algo:extract:{}'.format(
            self.default_redis_key)

        if not load_config:
            load_config = build_publish_request.build_publish_request()
        if not extract_config:
            extract_config = build_publish_request.build_publish_request()
        if not history_config:
            history_config = build_publish_request.build_publish_request()
        if not report_config:
            report_config = build_publish_request.build_publish_request()

        if not load_from_s3_bucket:
            load_from_s3_bucket = ae_consts.ALGO_READY_DATASET_S3_BUCKET_NAME
        if not extract_s3_bucket:
            extract_s3_bucket = ae_consts.ALGO_EXTRACT_DATASET_S3_BUCKET_NAME
        if not history_s3_bucket:
            history_s3_bucket = ae_consts.ALGO_HISTORY_DATASET_S3_BUCKET_NAME
        if not report_s3_bucket:
            report_s3_bucket = ae_consts.ALGO_REPORT_DATASET_S3_BUCKET_NAME

        # Load the input dataset publishing member variables
        self.extract_output_dir = extract_config.get(
            'output_dir', None)
        self.extract_output_file = extract_config.get(
            'output_file', None)
        self.extract_label = extract_config.get(
            'label', self.name)
        self.extract_convert_to_json = extract_config.get(
            'convert_to_json', True)
        self.extract_compress = extract_config.get(
            'compress', ae_consts.ALGO_INPUT_COMPRESS)
        self.extract_redis_enabled = extract_config.get(
            'redis_enabled', False)
        self.extract_redis_address = extract_config.get(
            'redis_address', ae_consts.ENABLED_S3_UPLOAD)
        self.extract_redis_db = extract_config.get(
            'redis_db', ae_consts.REDIS_DB)
        self.extract_redis_password = extract_config.get(
            'redis_password', ae_consts.REDIS_PASSWORD)
        self.extract_redis_expire = extract_config.get(
            'redis_expire', ae_consts.REDIS_EXPIRE)
        self.extract_redis_serializer = extract_config.get(
            'redis_serializer', 'json')
        self.extract_redis_encoding = extract_config.get(
            'redis_encoding', 'utf-8')
        self.extract_s3_enabled = extract_config.get(
            's3_enabled', False)
        self.extract_s3_address = extract_config.get(
            's3_address', ae_consts.S3_ADDRESS)
        self.extract_s3_bucket = extract_config.get(
            's3_bucket', extract_s3_bucket)
        self.extract_s3_access_key = extract_config.get(
            's3_access_key', ae_consts.S3_ACCESS_KEY)
        self.extract_s3_secret_key = extract_config.get(
            's3_secret_key', ae_consts.S3_SECRET_KEY)
        self.extract_s3_region_name = extract_config.get(
            's3_region_name', ae_consts.S3_REGION_NAME)
        self.extract_s3_secure = extract_config.get(
            's3_secure', ae_consts.S3_SECURE)
        self.extract_slack_enabled = extract_config.get(
            'slack_enabled', False)
        self.extract_slack_code_block = extract_config.get(
            'slack_code_block', False)
        self.extract_slack_full_width = extract_config.get(
            'slack_full_width', False)
        self.extract_redis_key = extract_config.get(
            'redis_key', extract_redis_key)
        self.extract_s3_key = extract_config.get(
            's3_key', extract_s3_key)
        self.extract_verbose = extract_config.get(
            'verbose', False)

        # load the trade history publishing member variables
        self.history_output_dir = history_config.get(
            'output_dir', None)
        self.history_output_file = history_config.get(
            'output_file', None)
        self.history_label = history_config.get(
            'label', self.name)
        self.history_convert_to_json = history_config.get(
            'convert_to_json', True)
        self.history_compress = history_config.get(
            'compress', ae_consts.ALGO_HISTORY_COMPRESS)
        self.history_redis_enabled = history_config.get(
            'redis_enabled', False)
        self.history_redis_address = history_config.get(
            'redis_address', ae_consts.ENABLED_S3_UPLOAD)
        self.history_redis_db = history_config.get(
            'redis_db', ae_consts.REDIS_DB)
        self.history_redis_password = history_config.get(
            'redis_password', ae_consts.REDIS_PASSWORD)
        self.history_redis_expire = history_config.get(
            'redis_expire', ae_consts.REDIS_EXPIRE)
        self.history_redis_serializer = history_config.get(
            'redis_serializer', 'json')
        self.history_redis_encoding = history_config.get(
            'redis_encoding', 'utf-8')
        self.history_s3_enabled = history_config.get(
            's3_enabled', False)
        self.history_s3_address = history_config.get(
            's3_address', ae_consts.S3_ADDRESS)
        self.history_s3_bucket = history_config.get(
            's3_bucket', history_s3_bucket)
        self.history_s3_access_key = history_config.get(
            's3_access_key', ae_consts.S3_ACCESS_KEY)
        self.history_s3_secret_key = history_config.get(
            's3_secret_key', ae_consts.S3_SECRET_KEY)
        self.history_s3_region_name = history_config.get(
            's3_region_name', ae_consts.S3_REGION_NAME)
        self.history_s3_secure = history_config.get(
            's3_secure', ae_consts.S3_SECURE)
        self.history_slack_enabled = history_config.get(
            'slack_enabled', False)
        self.history_slack_code_block = history_config.get(
            'slack_code_block', False)
        self.history_slack_full_width = history_config.get(
            'slack_full_width', False)
        self.history_redis_key = history_config.get(
            'redis_key', history_redis_key)
        self.history_s3_key = history_config.get(
            's3_key', history_s3_key)
        self.history_verbose = history_config.get(
            'verbose', False)

        # Load publishing for algorithm-generated report member variables
        self.report_output_dir = report_config.get(
            'output_dir', None)
        self.report_output_file = report_config.get(
            'output_file', None)
        self.report_label = report_config.get(
            'label', self.name)
        self.report_convert_to_json = report_config.get(
            'convert_to_json', True)
        self.report_compress = report_config.get(
            'compress', ae_consts.ALGO_REPORT_COMPRESS)
        self.report_redis_enabled = report_config.get(
            'redis_enabled', False)
        self.report_redis_address = report_config.get(
            'redis_address', ae_consts.ENABLED_S3_UPLOAD)
        self.report_redis_db = report_config.get(
            'redis_db', ae_consts.REDIS_DB)
        self.report_redis_password = report_config.get(
            'redis_password', ae_consts.REDIS_PASSWORD)
        self.report_redis_expire = report_config.get(
            'redis_expire', ae_consts.REDIS_EXPIRE)
        self.report_redis_serializer = report_config.get(
            'redis_serializer', 'json')
        self.report_redis_encoding = report_config.get(
            'redis_encoding', 'utf-8')
        self.report_s3_enabled = report_config.get(
            's3_enabled', False)
        self.report_s3_address = report_config.get(
            's3_address', ae_consts.S3_ADDRESS)
        self.report_s3_bucket = report_config.get(
            's3_bucket', report_s3_bucket)
        self.report_s3_access_key = report_config.get(
            's3_access_key', ae_consts.S3_ACCESS_KEY)
        self.report_s3_secret_key = report_config.get(
            's3_secret_key', ae_consts.S3_SECRET_KEY)
        self.report_s3_region_name = report_config.get(
            's3_region_name', ae_consts.S3_REGION_NAME)
        self.report_s3_secure = report_config.get(
            's3_secure', ae_consts.S3_SECURE)
        self.report_slack_enabled = report_config.get(
            'slack_enabled', False)
        self.report_slack_code_block = report_config.get(
            'slack_code_block', False)
        self.report_slack_full_width = report_config.get(
            'slack_full_width', False)
        self.report_redis_key = report_config.get(
            'redis_key', report_redis_key)
        self.report_s3_key = report_config.get(
            's3_key', report_s3_key)
        self.report_verbose = report_config.get(
            'verbose', False)

        self.loaded_dataset = None

        # load the algorithm-ready dataset input member variables
        self.dsload_output_dir = load_config.get(
            'output_dir', None)
        self.dsload_output_file = load_config.get(
            'output_file', None)
        self.dsload_label = load_config.get(
            'label', self.name)
        self.dsload_convert_to_json = load_config.get(
            'convert_to_json', True)
        self.dsload_compress = load_config.get(
            'compress', load_compress)
        self.dsload_redis_enabled = load_config.get(
            'redis_enabled', False)
        self.dsload_redis_address = load_config.get(
            'redis_address', ae_consts.ENABLED_S3_UPLOAD)
        self.dsload_redis_db = load_config.get(
            'redis_db', ae_consts.REDIS_DB)
        self.dsload_redis_password = load_config.get(
            'redis_password', ae_consts.REDIS_PASSWORD)
        self.dsload_redis_expire = load_config.get(
            'redis_expire', ae_consts.REDIS_EXPIRE)
        self.dsload_redis_serializer = load_config.get(
            'redis_serializer', 'json')
        self.dsload_redis_encoding = load_config.get(
            'redis_encoding', 'utf-8')
        self.dsload_s3_enabled = load_config.get(
            's3_enabled', False)
        self.dsload_s3_address = load_config.get(
            's3_address', ae_consts.S3_ADDRESS)
        self.dsload_s3_bucket = load_config.get(
            's3_bucket', load_from_s3_bucket)
        self.dsload_s3_access_key = load_config.get(
            's3_access_key', ae_consts.S3_ACCESS_KEY)
        self.dsload_s3_secret_key = load_config.get(
            's3_secret_key', ae_consts.S3_SECRET_KEY)
        self.dsload_s3_region_name = load_config.get(
            's3_region_name', ae_consts.S3_REGION_NAME)
        self.dsload_s3_secure = load_config.get(
            's3_secure', ae_consts.S3_SECURE)
        self.dsload_slack_enabled = load_config.get(
            'slack_enabled', False)
        self.dsload_slack_code_block = load_config.get(
            'slack_code_block', False)
        self.dsload_slack_full_width = load_config.get(
            'slack_full_width', False)
        self.dsload_redis_key = load_config.get(
            'redis_key', load_from_redis_key)
        self.dsload_s3_key = load_config.get(
            's3_key', load_from_s3_key)
        self.dsload_verbose = load_config.get(
            'verbose', False)

        self.load_from_external_source()

        if self.config_dict:
            self.timeseries = self.config_dict.get(
                'timeseries',
                'day').lower()
            self.trade_horizon = int(self.config_dict.get(
                'trade_horizon',
                '5'))
        # end of loading initial values from a config_dict before derived

        self.iproc = None
        self.iproc_label = 'no-iproc-label'
        self.num_indicators = 0
        self.latest_ind_report = None
        self.latest_buys = []  # latest indicators saying buy
        self.latest_sells = []  # latest indicators saying sell
        self.num_latest_buys = 0  # latest number of indicators saying buy
        self.num_latest_sells = 0  # latest number of indicators saying sell
        self.min_buy_indicators = 0
        self.min_sell_indicators = 0
        self.buy_rules = {}
        self.sell_rules = {}
        self.buy_shares = None
        self.is_live_trading = False
        self.found_minute_data = False
        self.use_minute = None
        self.intraday_start_min = None
        self.intraday_end_min = None
        self.intraday_events = {}

        self.ignore_history_keys = [
            'total_buys',
            'total_sells'
        ]
        self.ind_conf_ignore_keys = [
            'buys',
            'date',
            'id',
            'sells',
            'ticker'
        ]
        self.buy_reason = None
        self.sell_reason = None

        """
        if this is in a juptyer notebook
        this will show the plots at the end of
        each day... please avoid with
        the command line as the plot's window
        will block the algorithm until the window
        is closed
        """
        self.show_balance = ae_consts.ev(
            'SHOW_ALGO_BALANCE',
            '0') == '1'
        self.red_column = 'close'
        self.blue_column = 'balance'
        self.green_column = None
        self.orange_column = None
        self.net_value = self.starting_balance
        self.net_gain = self.net_value

        self.load_from_config(
            config_dict=self.config_dict)

        self.starting_balance = self.balance
        self.net_value = self.starting_balance
        self.net_gain = self.net_value

        self.timeseries = str(self.timeseries).lower()
        if self.timeseries == 'day':
            self.timeseries_value = ae_consts.ALGO_TIMESERIES_DAY
        elif self.timeseries == 'daily':
            self.timeseries_value = ae_consts.ALGO_TIMESERIES_DAY
        elif self.timeseries == 'minute':
            self.timeseries_value = ae_consts.ALGO_TIMESERIES_MINUTE
        elif self.timeseries == 'intraday':
            self.timeseries_value = ae_consts.ALGO_TIMESERIES_MINUTE
        else:
            self.timeseries_value = ae_consts.ALGO_TIMESERIES_MINUTE

        self.trade_strategy = str(self.trade_strategy).lower()
        self.trade_off_num_indicators = False
        if self.trade_strategy == 'count':
            self.trade_off_num_indicators = True
        else:
            self.trade_off_num_indicators = True

        # build the IndicatorProcessor after loading
        # values from an optional config_dict
        self.iproc = self.get_indicator_processor()
        if self.iproc:
            if not hasattr(self.iproc, 'process'):
                raise Exception(
                    '{} - Please implement a process methond in the '
                    'IndicatorProcessor - the current object={} '
                    'is missing one. Please refer to the example: '
                    'https://github.com/AlgoTraders/stock-analys'
                    'is-engine/blob/master/analysis_engine/indica'
                    'tors/indicator_processor.py'.format(
                        self.name,
                        self.iproc))
            self.iproc_label = self.iproc.get_label()
            self.num_indicators = self.iproc.get_num_indicators()
            self.min_buy_indicators = self.buy_rules.get(
                'min_indicators',
                None)
            self.min_sell_indicators = self.sell_rules.get(
                'min_indicators',
                None)
        # if indicator_processor exists

    # end of __init__

    def view_date_dataset_records(
            self,
            algo_id,
            ticker,
            node):
        """view_date_dataset_records

        View the dataset contents for a single node - use it with
        the algo config_dict by setting:

        ::

            "run_this_date": <string date YYYY-MM-DD>

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param node: dataset to process
        """
        # this will happen twice

        self.load_from_dataset(
            ds_data=node)
        self.inspect_dataset(
            algo_id=algo_id,
            ticker=ticker,
            dataset=node)
        if self.timeseries == 'minute':
            if len(self.df_minute.index) <= 1:
                log.error(
                    'EMPTY minute dataset')
                if self.raise_on_err:
                    raise Exception(
                        'EMPTY minute dataset')
                return
            for i, row in self.df_minute.iterrows():
                log.info(
                    'minute={} date={} close={}'.format(
                        i,
                        row['date'],
                        row['close']))
            log.info(
                'minute df len={}'.format(
                    len(self.df_minute.index)))
        elif self.timeseries == 'day':
            if len(self.df_daily.index) == 0:
                log.error(
                    'EMPTY daily dataset')
                if self.raise_on_err:
                    raise Exception(
                        'EMPTY minute dataset')
                return
            if hasattr(self.daily, 'to_json'):
                for i, row in self.df_daily.iterrows():
                    log.info(
                        'day={} date={} close={}'.format(
                            i,
                            row['date'],
                            row['close']))
                log.info(
                    'day df len={}'.format(
                        len(self.daily.index)))
    # end of view_date_dataset_records

    def get_indicator_processor(
            self,
            existing_processor=None):
        """get_indicator_processor

        singleton for getting the indicator processor

        :param existing_processor: allow derived algos
            to build their own indicator
            processor and pass it to the base
        """
        if existing_processor:
            if self.verbose:
                log.info(
                    '{} - loading existing processor={}'.format(
                        self.name,
                        existing_processor.get_name()))
            self.iproc = existing_processor
        else:
            if self.iproc:
                return self.iproc

            if not self.config_dict:
                if self.verbose:
                    log.info(
                        '{} - is missing an algorithm config_dict '
                        'please add one to run indicators'.format(
                            self.name))
            else:
                self.iproc = ind_processor.IndicatorProcessor(
                    config_dict=self.config_dict,
                    label='{}-prc'.format(
                        self.name),
                    verbose=self.verbose_processor)
        # if use new or existing

        return self.iproc
    # end of get_indicator_processor

    def get_indicator_process_last_indicator(
            self):
        """get_indicator_process_last_indicator

        Used to pull the indicator object back up
        to any created ``analysis_engine.algo.BaseAlgo`` objects

        .. tip:: this is for debugging data and code issues inside an
            indicator
        """
        return self.get_indicator_processor().get_last_ind_obj()
    # end of get_indicator_process_last_indicator

    def inspect_dataset(
            self,
            algo_id,
            ticker,
            dataset):
        """inspect_dataset

        Use this method inside of an algorithm's ``process()`` method
        to view the available datasets in the redis cache

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
        """
        log.info('--------------')
        log.info(
            'process(algo_id={}, ticker={}, '
            'data:'.format(
                algo_id,
                ticker))
        for k in dataset:
            log.info(
                'main keys={}'.format(
                    k))
        for k in dataset['data']:
            if hasattr(dataset['data'][k], 'to_json'):
                log.info(
                    'data key={} contains a pandas.DataFrame with '
                    'rows={}'.format(
                        k,
                        len(dataset['data'][k].index)))
            else:
                log.info(
                    'data key={} contains a pandas.DataFrame with '
                    'rows=0'.format(
                       k))
    # end of inspect_dataset

    def process(
            self,
            algo_id,
            ticker,
            dataset):
        """process

        Derive custom algorithm buy and sell conditions
        before placing orders. Just implement your own
        ``process`` method.

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
            multiple pandas ``pandas.DataFrame`` objects. Dictionary where keys
            represent a label from one of the data sources (``IEX``,
            ``Yahoo``, ``FinViz`` or other). Here is the supported
            dataset structure for the process method:

            .. note:: There are no required keys for ``data``, the list
                below is not hard-enforced by default. This is just
                a reference for what is available with the v1 engine.

            ::

                dataset = {
                    'id': <string TICKER_DATE - redis cache key>,
                    'date': <string DATE>,
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

            example:

            ::

                dataset = {
                    'id': 'SPY_2018-11-02
                    'date': '2018-11-02',
                    'data': {
                        'daily': pd.DataFrame,
                        'minute': pd.DataFrame,
                        'calls': pd.DataFrame,
                        'puts': pd.DataFrame,
                        'news': pd.DataFrame
                    }
                }
        """

        log.info(
            'process - ticker={} balance={} owned={} date={} '
            'high={} low={} open={} close={} vol={} '
            'comm={} '
            'buy_str={} buy_risk={} '
            'sell_str={} sell_risk={} '
            'num_buys={} num_sells={} '
            'id={}'.format(
                self.ticker,
                self.balance,
                self.num_owned,
                self.trade_date,
                self.latest_high,
                self.latest_low,
                self.latest_open,
                self.latest_close,
                self.latest_volume,
                self.commission,
                self.buy_strength,
                self.buy_risk,
                self.sell_strength,
                self.sell_risk,
                len(self.buys),
                len(self.sells),
                algo_id))

        # flip these on to sell/buy
        # buys will not FILL if there's not enough funds to buy
        # sells will not FILL if there's nothing already owned
        self.should_sell = False
        self.should_buy = False

        log.info(
            '{} - ready with process has df_daily '
            'rows={} num_owned={} '
            'indicator_buys={} min_buy={} '
            'indicator_sells={} min_sell={}'.format(
                self.name,
                len(self.df_daily.index),
                self.num_owned,
                self.num_latest_buys,
                self.min_buy_indicators,
                self.num_latest_sells,
                self.min_sell_indicators))

        """
        Want to iterate over daily pricing data
        to determine buys or sells from the:
        self.df_daily dataset fetched from IEX?

        # loop over the rows in the daily dataset:
        for idx, row in self.df_daily.iterrows():
            print(row)
        """
    # end of process

    def trade_off_indicator_buy_and_sell_signals(
            self,
            ticker,
            algo_id,
            reason_for_buy=None,
            reason_for_sell=None):
        """trade_off_indicator_buy_and_sell_signals

        Check if the minimum number of indicators
        for a buy or a sell were found. If there
        were, then commit the trade.

        .. code-block:: python

            if self.trade_off_num_indicators:
                if self.num_latest_buys >= self.min_buy_indicators:
                    self.should_buy = True
                elif self.num_latest_sells >= self.min_sell_indicators:
                    self.should_sell = True

        :param ticker: ticker symbol
        :param algo_id: string algo for tracking
            internal progress for debugging
        :param reason_for_buy: optional - string
            for tracking why the algo bought
        :param reason_for_sell: optional - string
            for tracking why the algo sold
        """

        if self.trade_off_num_indicators:
            if self.num_latest_buys >= self.min_buy_indicators:
                self.should_buy = True
            elif self.num_latest_sells >= self.min_sell_indicators:
                self.should_sell = True

        if self.num_owned and self.should_sell:
            if self.verbose_trading or self.verbose:
                log.critical(
                    'TRADE - SELLDECISION - '
                    '{} '
                    'trade_off_num={} '
                    'num_sells={} > min_sells={} '
                    'should_sell={}'.format(
                        algo_id,
                        self.trade_off_num_indicators,
                        self.num_latest_sells,
                        self.min_sell_indicators,
                        self.should_sell))

            self.create_sell_order(
                ticker=ticker,
                shares=self.num_owned,
                minute=self.use_minute,
                row={
                    'name': algo_id,
                    'close': self.latest_close,
                    'date': self.trade_date
                },
                is_live_trading=self.is_live_trading,
                reason=reason_for_buy)
        # if own shares and should sell
        # else if should buy:
        elif self.should_buy:
            if self.verbose_trading or self.verbose:
                log.critical(
                    'TRADE - BUYDECISION - '
                    '{} '
                    'trade_off_num={} '
                    'num_buys={} > min_buys={} '
                    'should_buy={}'.format(
                        algo_id,
                        self.trade_off_num_indicators,
                        self.num_latest_buys,
                        self.min_buy_indicators,
                        self.should_buy))
            self.create_buy_order(
                ticker=ticker,
                shares=self.buy_shares,
                minute=self.use_minute,
                row={
                    'name': algo_id,
                    'close': self.latest_close,
                    'date': self.trade_date
                },
                is_live_trading=self.is_live_trading,
                reason=reason_for_sell)
        # end of should_buy

    # end of trade_off_indicator_buy_and_sell_signals

    def load_from_external_source(
            self,
            path_to_file=None,
            s3_bucket=None,
            s3_key=None,
            redis_key=None):
        """load_from_external_source

        Load an algorithm-ready dataset for ``handle_data`` backtesting
        and trade performance analysis from:

        - Local file
        - S3
        - Redis

        :param path_to_file: optional - path to local file
        :param s3_bucket: optional - s3 s3_bucket
        :param s3_key: optional - s3 key
        :param redis_key: optional - redis key
        """

        if path_to_file:
            self.dsload_output_file = path_to_file
        if s3_key:
            self.dsload_s3_key = s3_key
        if s3_bucket:
            self.dsload_s3_bucket = s3_bucket
            self.dsload_s3_enabled = True
        if redis_key:
            self.dsload_redis_key = redis_key
            self.dsload_redis_enabled = True

        if (self.dsload_s3_key and
                self.dsload_s3_bucket and
                self.dsload_s3_enabled and
                not self.loaded_dataset):
            self.debug_msg = (
                'external load START - s3={}:{}/{}'.format(
                    self.dsload_s3_address,
                    self.dsload_s3_bucket,
                    self.dsload_s3_key))
            if self.verbose:
                log.info(self.debug_msg)
            self.loaded_dataset = load_dataset.load_dataset(
                s3_enabled=self.dsload_s3_enabled,
                s3_address=self.dsload_s3_address,
                s3_key=self.dsload_s3_key,
                s3_bucket=self.dsload_s3_bucket,
                s3_access_key=self.dsload_s3_access_key,
                s3_secret_key=self.dsload_s3_secret_key,
                s3_region_name=self.dsload_s3_region_name,
                s3_secure=self.dsload_s3_secure,
                compress=self.dsload_compress,
                encoding=self.dsload_redis_encoding)
            if self.loaded_dataset:
                self.debug_msg = (
                    'external load SUCCESS - s3={}:{}/{}'.format(
                        self.dsload_s3_address,
                        self.dsload_s3_bucket,
                        self.dsload_s3_key))
            else:
                self.debug_msg = (
                    'external load FAILED - s3={}:{}/{}'.format(
                        self.dsload_s3_address,
                        self.dsload_s3_bucket,
                        self.dsload_s3_key))
                log.error(self.debug_msg)
                raise Exception(self.debug_msg)
        elif (self.dsload_redis_key and
                self.dsload_redis_enabled and
                not self.loaded_dataset):
            self.debug_msg = (
                'external load START - redis={}:{}/{}'.format(
                    self.dsload_redis_address,
                    self.dsload_redis_db,
                    self.dsload_redis_key))
            log.debug(self.debug_msg)
            self.loaded_dataset = load_dataset.load_dataset(
                redis_enabled=self.dsload_redis_enabled,
                redis_address=self.dsload_redis_address,
                redis_key=self.dsload_redis_key,
                redis_db=self.dsload_redis_db,
                redis_password=self.dsload_redis_password,
                redis_expire=self.dsload_redis_expire,
                redis_serializer=self.dsload_redis_serializer,
                redis_encoding=self.dsload_redis_encoding,
                compress=self.dsload_compress,
                encoding=self.dsload_redis_encoding)
            if self.loaded_dataset:
                self.debug_msg = (
                    'external load SUCCESS - redis={}:{}/{}'.format(
                        self.dsload_redis_address,
                        self.dsload_redis_db,
                        self.dsload_redis_key))
            else:
                self.debug_msg = (
                    'external load FAILED - redis={}:{}/{}'.format(
                        self.dsload_redis_address,
                        self.dsload_redis_db,
                        self.dsload_redis_key))
                log.error(self.debug_msg)
                raise Exception(self.debug_msg)
        elif (self.dsload_output_file and
                not self.loaded_dataset):
            if os.path.exists(self.dsload_output_file):
                self.debug_msg = (
                    'external load START - file={}'.format(
                        self.dsload_output_file))
                log.debug(self.debug_msg)
                self.loaded_dataset = load_dataset.load_dataset(
                    path_to_file=self.dsload_output_file,
                    compress=self.dsload_compress,
                    encoding=self.extract_redis_encoding)
                if self.loaded_dataset:
                    self.debug_msg = (
                        'external load SUCCESS - file={}'.format(
                            self.dsload_output_file))
                else:
                    self.debug_msg = (
                        'external load FAILED - file={}'.format(
                            self.dsload_output_file))
                    log.error(self.debug_msg)
                    raise Exception(self.debug_msg)
            else:
                self.debug_msg = (
                    'external load - did not find file={}'.format(
                        self.dsload_output_file))
                log.error(self.debug_msg)
                raise Exception(self.debug_msg)
        # end of if supported external loader
        log.debug(
            'external load END')
    # end of load_from_external_source

    def publish_report_dataset(
            self,
            **kwargs):
        """publish_report_dataset

        publish trade history datasets to caches (redis), archives
        (minio s3), a local file (``output_file``) and slack

        :param kwargs: keyword argument dictionary
        :return: tuple: ``status``, ``output_file``
        """

        # parse optional input args
        output_file = kwargs.get(
            'output_file', None)
        label = kwargs.get(
            'label', self.name)
        convert_to_json = kwargs.get(
            'convert_to_json', self.report_convert_to_json)
        compress = kwargs.get(
            'compress', self.report_compress)
        redis_enabled = kwargs.get(
            'redis_enabled', False)
        redis_address = kwargs.get(
            'redis_address', self.report_redis_address)
        redis_db = kwargs.get(
            'redis_db', self.report_redis_db)
        redis_password = kwargs.get(
            'redis_password', self.report_redis_password)
        redis_expire = kwargs.get(
            'redis_expire', self.report_redis_expire)
        redis_serializer = kwargs.get(
            'redis_serializer', self.report_redis_serializer)
        redis_encoding = kwargs.get(
            'redis_encoding', self.report_redis_encoding)
        s3_enabled = kwargs.get(
            's3_enabled', False)
        s3_address = kwargs.get(
            's3_address', self.report_s3_address)
        s3_bucket = kwargs.get(
            's3_bucket', self.report_s3_bucket)
        s3_access_key = kwargs.get(
            's3_access_key', self.report_s3_access_key)
        s3_secret_key = kwargs.get(
            's3_secret_key', self.report_s3_secret_key)
        s3_region_name = kwargs.get(
            's3_region_name', self.report_s3_region_name)
        s3_secure = kwargs.get(
            's3_secure', self.report_s3_secure)
        slack_enabled = kwargs.get(
            'slack_enabled', self.report_slack_enabled)
        slack_code_block = kwargs.get(
            'slack_code_block', self.report_slack_code_block)
        slack_full_width = kwargs.get(
            'slack_full_width', self.report_slack_full_width)
        redis_key = kwargs.get(
            'redis_key', self.report_redis_key)
        s3_key = kwargs.get(
            's3_key', self.report_s3_key)
        verbose = kwargs.get(
            'verbose', self.report_verbose)

        status = ae_consts.NOT_RUN

        if not self.publish_report:
            if self.verbose:
                log.info(
                    'report publish - disabled - '
                    '{} - tickers={}'.format(
                        self.name,
                        self.tickers))
            return status

        output_record = self.create_report_dataset()

        if output_file or s3_enabled or redis_enabled or slack_enabled:
            if self.verbose:
                log.info(
                    'report build json - {} - tickers={}'.format(
                        self.name,
                        self.tickers))
                use_data = json.dumps(output_record)
            num_bytes = len(use_data)
            num_mb = ae_consts.get_mb(num_bytes)
            log.info(
                'report publish - START - '
                '{} - tickers={} '
                'file={} size={}MB '
                's3={} s3_key={} '
                'redis={} redis_key={} '
                'slack={}'.format(
                    self.name,
                    self.tickers,
                    output_file,
                    num_mb,
                    s3_enabled,
                    s3_key,
                    redis_enabled,
                    redis_key,
                    slack_enabled))
            publish_status = publish.publish(
                data=use_data,
                label=label,
                convert_to_json=convert_to_json,
                output_file=output_file,
                compress=compress,
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
                s3_bucket=s3_bucket,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_region_name=s3_region_name,
                s3_secure=s3_secure,
                slack_enabled=slack_enabled,
                slack_code_block=slack_code_block,
                slack_full_width=slack_full_width,
                verbose=verbose)

            status = publish_status

            log.info(
                'report publish - END - {} '
                '{} - tickers={} '
                'file={} s3={} redis={} size={}MB'.format(
                    ae_consts.get_status(status=status),
                    self.name,
                    self.tickers,
                    output_file,
                    s3_key,
                    redis_key,
                    num_mb))
        else:
            if self.verbose:
                log.info(
                    '{} - report not publishing for output_file={} '
                    's3_enabled={} redis_enabled={} '
                    'slack_enabled={}'.format(
                        self.name,
                        output_file,
                        s3_enabled,
                        redis_enabled,
                        slack_enabled))
        # end of handling for publish

        return status
    # end of publish_report_dataset

    def create_report_dataset(
            self):
        """create_report_dataset

        Create the ``Trading Performance Report`` dataset
        during the ``self.publish_input_dataset()`` member method.
        Inherited Algorithm classes can derive how they build a
        custom ``Trading Performance Report`` dataset before publishing
        by implementing this method in the derived class.
        """

        if self.verbose:
            log.info('report - create start')

        if self.last_handle_data:
            data_for_tickers = self.get_supported_tickers_in_data(
                data=self.last_handle_data)
        else:
            data_for_tickers = self.tickers

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            self.debug_msg = (
                '{} handle - tickers={}'.format(
                    self.name,
                    json.dumps(data_for_tickers)))

        output_record = {}
        for ticker in data_for_tickers:
            if ticker not in output_record:
                output_record[ticker] = []
            num_ticker_datasets = len(self.last_handle_data[ticker])
            cur_idx = 1
            for idx, node in enumerate(self.last_handle_data[ticker]):
                track_label = self.build_progress_label(
                    progress=cur_idx,
                    total=num_ticker_datasets)
                algo_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                if self.verbose:
                    log.info(
                        '{} report - {} - ds={}'.format(
                            self.name,
                            algo_id,
                            node['date']))

                    new_node = {
                        'id': node['id'],
                        'date': node['date'],
                        'data': {}
                    }

                output_record[ticker].append(new_node)
                cur_idx += 1
            # end for all self.last_handle_data[ticker]
        # end of converting dataset

        return output_record
    # end of create_report_dataset

    def publish_trade_history_dataset(
            self,
            **kwargs):
        """publish_trade_history_dataset

        publish trade history datasets to caches (redis), archives
        (minio s3), a local file (``output_file``) and slack

        :param kwargs: keyword argument dictionary
        :return: tuple: ``status``, ``output_file``
        """

        # parse optional input args
        output_file = kwargs.get(
            'output_file', None)
        label = kwargs.get(
            'label', self.name)
        convert_to_json = kwargs.get(
            'convert_to_json', self.history_convert_to_json)
        compress = kwargs.get(
            'compress', self.history_compress)
        redis_enabled = kwargs.get(
            'redis_enabled', False)
        redis_address = kwargs.get(
            'redis_address', self.history_redis_address)
        redis_db = kwargs.get(
            'redis_db', self.history_redis_db)
        redis_password = kwargs.get(
            'redis_password', self.history_redis_password)
        redis_expire = kwargs.get(
            'redis_expire', self.history_redis_expire)
        redis_serializer = kwargs.get(
            'redis_serializer', self.history_redis_serializer)
        redis_encoding = kwargs.get(
            'redis_encoding', self.history_redis_encoding)
        s3_enabled = kwargs.get(
            's3_enabled', False)
        s3_address = kwargs.get(
            's3_address', self.history_s3_address)
        s3_bucket = kwargs.get(
            's3_bucket', self.history_s3_bucket)
        s3_access_key = kwargs.get(
            's3_access_key', self.history_s3_access_key)
        s3_secret_key = kwargs.get(
            's3_secret_key', self.history_s3_secret_key)
        s3_region_name = kwargs.get(
            's3_region_name', self.history_s3_region_name)
        s3_secure = kwargs.get(
            's3_secure', self.history_s3_secure)
        slack_enabled = kwargs.get(
            'slack_enabled', self.history_slack_enabled)
        slack_code_block = kwargs.get(
            'slack_code_block', self.history_slack_code_block)
        slack_full_width = kwargs.get(
            'slack_full_width', self.history_slack_full_width)
        redis_key = kwargs.get(
            'redis_key', self.history_redis_key)
        s3_key = kwargs.get(
            's3_key', self.history_s3_key)
        verbose = kwargs.get(
            'verbose', self.history_verbose)
        add_metrics_to_key = kwargs.get(
            'add_metrics_to_key', False)

        status = ae_consts.NOT_RUN

        if not self.publish_history:
            log.info(
                'history publish - disabled - '
                '{} - tickers={}'.format(
                    self.name,
                    self.tickers))
            return status
        # end of screening for returning early

        output_record = self.create_history_dataset()

        if output_file or s3_enabled or redis_enabled or slack_enabled:
            if self.verbose:
                log.info(
                    'history build json - {} - tickers={}'.format(
                        self.name,
                        self.tickers))

            # for mass trade history publishing, make it
            # easy to find the best-of runs
            if add_metrics_to_key:
                (self.num_owned,
                 self.ticker_buys,
                 self.ticker_sells) = self.get_ticker_positions(
                    ticker=self.tickers[0])

                status_str = 'NEGATIVE'
                if self.net_gain > 0:
                    status_str = 'POSITIVE'

                now = datetime.datetime.utcnow()
                seconds = ae_consts.to_f((
                    now - self.created_on_date).total_seconds())

                # https://stackoverflow.com/questions/6870824/
                # what-is-the-maximum-length-of-a-filename-in-s3
                # 1024 characters
                s3_key = (
                    '{}_netgain_{}_netvalue_'
                    '{}_'
                    '{}_startbalance_{}_endbalance_'
                    '{}_shares_{}_close_'
                    '{}_buys_{}_sells_'
                    '{}_minbuyinds_{}_minsellinds_'
                    '{}_seconds_'
                    '{}'.format(
                        ae_consts.to_f(self.net_gain),
                        ae_consts.to_f(self.net_value),
                        status_str,
                        ae_consts.to_f(self.starting_balance),
                        ae_consts.to_f(self.balance),
                        self.num_owned,
                        ae_consts.to_f(self.latest_close),
                        self.num_buys,
                        self.num_sells,
                        self.min_buy_indicators,
                        self.min_sell_indicators,
                        seconds,
                        s3_key))[0:1023]
            # end of if add metrics to key

            use_data = json.dumps(output_record)
            num_bytes = len(use_data)
            num_mb = ae_consts.get_mb(num_bytes)
            log.info(
                'history publish - START - '
                '{} - ticker={} '
                'file={} size={}MB '
                's3={}/{} s3_key={} '
                'redis={} redis_key={} '
                'slack={}'.format(
                    self.name,
                    self.tickers[0],
                    output_file,
                    num_mb,
                    s3_address,
                    s3_bucket,
                    s3_key,
                    redis_enabled,
                    redis_key,
                    slack_enabled))
            publish_status = publish.publish(
                data=use_data,
                label=label,
                convert_to_json=convert_to_json,
                output_file=output_file,
                compress=compress,
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
                s3_bucket=s3_bucket,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_region_name=s3_region_name,
                s3_secure=s3_secure,
                slack_enabled=slack_enabled,
                slack_code_block=slack_code_block,
                slack_full_width=slack_full_width,
                verbose=verbose)

            status = publish_status

            log.info(
                'history publish - END - {} '
                '{} - tickers={} '
                'file={} s3={} redis={} size={}MB'.format(
                    ae_consts.get_status(status=status),
                    self.name,
                    self.tickers,
                    output_file,
                    s3_key,
                    redis_key,
                    num_mb))
        else:
            if self.verbose:
                log.info(
                    '{} - history not publishing for output_file={} '
                    's3_enabled={} redis_enabled={} '
                    'slack_enabled={}'.format(
                        self.name,
                        output_file,
                        s3_enabled,
                        redis_enabled,
                        slack_enabled))
        # end of handling for publish

        return status
    # end of publish_trade_history_dataset

    def create_history_dataset(
            self):
        """create_history_dataset

        Create the ``Trading History`` dataset
        during the ``self.publish_trade_history_dataset()`` member method.
        Inherited Algorithm classes can derive how they build a
        custom ``Trading History`` dataset before publishing
        by implementing this method in the derived class.
        """

        if self.verbose:
            log.info('history - create start')

        if self.last_handle_data:
            data_for_tickers = self.get_supported_tickers_in_data(
                data=self.last_handle_data)
        else:
            data_for_tickers = self.tickers

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            self.debug_msg = (
                '{} handle - tickers={}'.format(
                    self.name,
                    json.dumps(data_for_tickers)))

        history_by_ticker = {}
        for ticker in data_for_tickers:
            ticker_history_rec_list = self.build_ticker_history(
                ticker=ticker,
                ignore_keys=self.ignore_history_keys)
            history_by_ticker[ticker] = ticker_history_rec_list
        # end for all tickers to filter

        output_record = {
            'tickers': data_for_tickers,
            'version': int(ae_consts.ALGO_HISTORY_VERSION),
            'last_trade_date': ae_utils.get_last_close_str(),
            'algo_config_dict': self.config_dict,
            'algo_name':  self.name,
            'created': ae_utils.utc_now_str()
        }
        for ticker in data_for_tickers:
            if ticker not in output_record:
                output_record[ticker] = []
            num_ticker_datasets = len(history_by_ticker[ticker])
            cur_idx = 1
            for idx, node in enumerate(history_by_ticker[ticker]):
                track_label = self.build_progress_label(
                    progress=cur_idx,
                    total=num_ticker_datasets)
                algo_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                if self.verbose:
                    log.info(
                        '{} history - {} - ds={}'.format(
                            self.name,
                            algo_id,
                            node.get(
                                'minute',
                                node.get(
                                    'date',
                                    'no-date-set'))))

                output_record[ticker].append(node)
                cur_idx += 1
            # end for all self.last_handle_data[ticker]
        # end of converting dataset

        return output_record
    # end of create_history_dataset

    def build_ticker_history(
            self,
            ticker,
            ignore_keys):
        """build_ticker_history

        For all records in ``self.order_history`` compile
        a filter list of history records per ``ticker`` while
        pruning any keys that are in the list of ``ignore_keys``

        :param ticker: string ticker symbol
        :param ignore_history_keys: list of
            keys to not include in the
            history report
        """
        history_for_ticker = []

        for org_node in self.order_history:
            status = org_node.get('status', ae_consts.INVALID)
            if status != ae_consts.INVALID:
                node = copy.deepcopy(org_node)
                is_valid = True
                for i in ignore_keys:
                    node.pop(i, None)
                if is_valid:
                    history_for_ticker.append(node)
        # end of all order history records

        return history_for_ticker
    # end of build_ticker_history

    def publish_input_dataset(
            self,
            **kwargs):
        """publish_input_dataset

        publish input datasets to caches (redis), archives
        (minio s3), a local file (``output_file``) and slack

        :param kwargs: keyword argument dictionary
        :return: tuple: ``status``, ``output_file``
        """

        # parse optional input args
        output_file = kwargs.get(
            'output_file', None)
        label = kwargs.get(
            'label', self.name)
        convert_to_json = kwargs.get(
            'convert_to_json', self.extract_convert_to_json)
        compress = kwargs.get(
            'compress', self.extract_compress)
        redis_enabled = kwargs.get(
            'redis_enabled', False)
        redis_address = kwargs.get(
            'redis_address', self.extract_redis_address)
        redis_db = kwargs.get(
            'redis_db', self.extract_redis_db)
        redis_password = kwargs.get(
            'redis_password', self.extract_redis_password)
        redis_expire = kwargs.get(
            'redis_expire', self.extract_redis_expire)
        redis_serializer = kwargs.get(
            'redis_serializer', self.extract_redis_serializer)
        redis_encoding = kwargs.get(
            'redis_encoding', self.extract_redis_encoding)
        s3_enabled = kwargs.get(
            's3_enabled', False)
        s3_address = kwargs.get(
            's3_address', self.extract_s3_address)
        s3_bucket = kwargs.get(
            's3_bucket', self.extract_s3_bucket)
        s3_access_key = kwargs.get(
            's3_access_key', self.extract_s3_access_key)
        s3_secret_key = kwargs.get(
            's3_secret_key', self.extract_s3_secret_key)
        s3_region_name = kwargs.get(
            's3_region_name', self.extract_s3_region_name)
        s3_secure = kwargs.get(
            's3_secure', self.extract_s3_secure)
        slack_enabled = kwargs.get(
            'slack_enabled', self.extract_slack_enabled)
        slack_code_block = kwargs.get(
            'slack_code_block', self.extract_slack_code_block)
        slack_full_width = kwargs.get(
            'slack_full_width', self.extract_slack_full_width)
        redis_key = kwargs.get(
            'redis_key', self.extract_redis_key)
        s3_key = kwargs.get(
            's3_key', self.extract_s3_key)
        verbose = kwargs.get(
            'verbose', self.extract_verbose)

        status = ae_consts.NOT_RUN

        if not self.publish_input:
            log.info(
                'input publish - disabled - '
                '{} - tickers={}'.format(
                    self.name,
                    self.tickers))
            return status

        output_record = self.create_algorithm_ready_dataset()

        if output_file or s3_enabled or redis_enabled or slack_enabled:
            if self.verbose:
                log.info(
                    'input build json - {} - tickers={}'.format(
                        self.name,
                        self.tickers))
            use_data = json.dumps(output_record)
            num_bytes = len(use_data)
            num_mb = ae_consts.get_mb(num_bytes)
            log.info(
                'input publish - START - '
                '{} - tickers={} '
                'file={} size={}MB '
                's3={} s3_key={} '
                'redis={} redis_key={} '
                'slack={}'.format(
                    self.name,
                    self.tickers,
                    output_file,
                    num_mb,
                    s3_enabled,
                    s3_key,
                    redis_enabled,
                    redis_key,
                    slack_enabled))
            publish_status = publish.publish(
                data=use_data,
                label=label,
                convert_to_json=convert_to_json,
                output_file=output_file,
                compress=compress,
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
                s3_bucket=s3_bucket,
                s3_access_key=s3_access_key,
                s3_secret_key=s3_secret_key,
                s3_region_name=s3_region_name,
                s3_secure=s3_secure,
                slack_enabled=slack_enabled,
                slack_code_block=slack_code_block,
                slack_full_width=slack_full_width,
                verbose=verbose)

            status = publish_status

            log.info(
                'input publish - END - {} '
                '{} - tickers={} '
                'file={} s3={} redis={} size={}MB'.format(
                    ae_consts.get_status(status=status),
                    self.name,
                    self.tickers,
                    output_file,
                    s3_key,
                    redis_key,
                    num_mb))
        # end of handling for publish

        return status
    # end of publish_input_dataset

    def create_algorithm_ready_dataset(
            self):
        """create_algorithm_ready_dataset

        Create the ``Algorithm-Ready`` dataset
        during the ``self.publish_input_dataset()`` member method.
        Inherited Algorithm classes can derive how they build a
        custom ``Algorithm-Ready`` dataset before publishing
        by implementing this method in the derived class.
        """

        if self.verbose:
            log.info('algo-ready - create start')

        data_for_tickers = self.get_supported_tickers_in_data(
            data=self.last_handle_data)

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            self.debug_msg = (
                '{} handle - tickers={}'.format(
                    self.name,
                    json.dumps(data_for_tickers)))

        output_record = {}
        for ticker in data_for_tickers:
            if ticker not in output_record:
                output_record[ticker] = []
            num_ticker_datasets = len(self.last_handle_data[ticker])
            cur_idx = 1
            for idx, node in enumerate(self.last_handle_data[ticker]):
                track_label = self.build_progress_label(
                    progress=cur_idx,
                    total=num_ticker_datasets)
                algo_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                if self.verbose:
                    log.info(
                        '{} convert - {} - ds={}'.format(
                            self.name,
                            algo_id,
                            node['date']))

                new_node = {
                    'id': node['id'],
                    'date': node['date'],
                    'data': {}
                }

                # parse the dataset node and set member variables
                self.debug_msg = (
                    '{} START - convert load dataset id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))
                self.load_from_dataset(
                    ds_data=node)
                for ds_key in node['data']:
                    empty_ds = self.empty_pd_str
                    data_val = node['data'][ds_key]
                    if ds_key not in new_node['data']:
                        new_node['data'][ds_key] = empty_ds
                    self.debug_msg = (
                        'convert node={} ds_key={}'.format(
                            node,
                            ds_key))
                    if hasattr(data_val, 'to_json'):
                        new_node['data'][ds_key] = data_val.to_json(
                            orient='records',
                            date_format='iso')
                    else:
                        if not data_val:
                            new_node['data'][ds_key] = empty_ds
                        else:
                            new_node['data'][ds_key] = json.dumps(
                                data_val)
                    # if/else
                # for all dataset values in data
                self.debug_msg = (
                    '{} END - convert load dataset id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))

                output_record[ticker].append(new_node)
                cur_idx += 1
            # end for all self.last_handle_data[ticker]
        # end of converting dataset

        return output_record
    # end of create_algorithm_ready_dataset

    def get_ticker_positions(
            self,
            ticker):
        """get_ticker_positions

        get the current positions for a ticker and
        returns a tuple:
        ``num_owned (integer), buys (list), sells (list)```

        .. code-block:: python

            num_owned, buys, sells = self.get_ticker_positions(
                ticker=ticker)

        :param ticker: ticker to lookup
        """
        buys = None
        sells = None
        num_owned = None
        self.num_buys = 0
        self.num_sells = 0
        if ticker in self.positions:
            num_owned = self.positions[ticker].get(
                'shares',
                None)
            buys = self.positions[ticker].get(
                'buys',
                [])
            sells = self.positions[ticker].get(
                'sells',
                [])
            self.num_buys = len(buys)
            self.num_sells = len(sells)
        # if own the ticker

        self.net_value = ae_consts.to_f(self.balance)
        if self.latest_close and num_owned:
            self.net_value = ae_consts.to_f(
                self.balance + (
                    num_owned * self.latest_close))

        self.net_gain = ae_consts.to_f(
            self.net_value - self.starting_balance)

        return num_owned, buys, sells
    # end of get_ticker_positions

    def get_trade_history_node(
                self):
        """get_trade_history_node

            Helper for quickly building a history node
            on a derived algorithm. Whatever member variables
            are in the base class ``analysis_engine.algo.BaseAlgo``
            will be added automatically into the returned:
            ``historical transaction dictionary``

            .. tip:: if you get a ``None`` back it means there
                could be a bug in how you are using the member
                variables (likely created an invalid math
                calculation) or could be a bug in the helper:
                `build_trade_history_entry <https://github.c
                om/AlgoTraders/stock-analysis-engine/blob/ma
                ster/analysis_engine/build_trade_history_entry.py>`__
        """
        history_dict = history_utils.build_trade_history_entry(
            ticker=self.ticker,
            algo_start_price=self.starting_close,
            original_balance=self.starting_balance,
            num_owned=self.num_owned,
            close=self.trade_price,
            balance=self.balance,
            commission=self.commission,
            date=self.trade_date,
            minute=self.use_minute,
            trade_type=self.trade_type,
            high=self.latest_high,
            low=self.latest_low,
            open_val=self.latest_open,
            volume=self.latest_volume,
            today_high=self.today_high,
            today_low=self.today_low,
            today_open_val=self.today_open,
            today_close=self.today_close,
            today_volume=self.today_volume,
            ask=self.ask,
            bid=self.bid,
            stop_loss=self.stop_loss,
            trailing_stop_loss=self.trailing_stop_loss,
            buy_hold_units=self.buy_hold_units,
            sell_hold_units=self.sell_hold_units,
            spread_exp_date=self.spread_exp_date,
            prev_balance=self.prev_bal,
            prev_num_owned=self.prev_num_owned,
            total_buys=self.num_buys,
            total_sells=self.num_sells,
            buy_triggered=self.should_buy,
            buy_strength=self.buy_strength,
            buy_risk=self.buy_risk,
            sell_triggered=self.should_sell,
            sell_strength=self.sell_strength,
            sell_risk=self.sell_risk,
            num_indicators_buy=self.num_latest_buys,
            num_indicators_sell=self.num_latest_sells,
            min_buy_indicators=self.min_buy_indicators,
            min_sell_indicators=self.min_sell_indicators,
            net_gain=self.net_gain,
            net_value=self.net_value,
            note=self.note,
            ds_id=self.ds_id,
            version=self.version)
        return history_dict
    # end of get_trade_history_node

    def load_from_config(
            self,
            config_dict):
        """load_from_config

        support for replaying algorithms from a trading history

        :param config_dict: algorithm configuration values
            usually from a previous trading history or for
            quickly testing dataset theories in a development
            environment
        """
        if config_dict:
            if not self.verbose:
                self.verbose = config_dict.get('verbose', False)
                for k in config_dict:
                    log.info(
                        'setting algo member={} to config value={}'
                        ''.format(
                            k))
                    self.__dict__[k] = config_dict[k]
            else:
                for k in config_dict:
                    self.__dict__[k] = config_dict[k]
        # end of loading config
    # end of load_from_config

    def get_name(self):
        """get_name"""
        return self.name
    # end of get_name

    def get_result(self):
        """get_result"""

        self.debug_msg = (
            'building results')
        finished_date = ae_utils.utc_now_str()
        self.result = {
            'name': self.name,
            'created': self.created_date,
            'updated': finished_date,
            'open_positions': self.positions,
            'buys': self.get_buys(),
            'sells': self.get_sells(),
            'num_processed': len(self.order_history),
            'history': self.order_history,
            'balance': self.balance,
            'commission': self.commission
        }

        return self.result
    # end of get_result

    def get_debug_msg(
            self):
        """get_debug_msg

        debug algorithms that failed
        by viewing the last ``self.debug_msg`` they
        set
        """
        return self.debug_msg
    # end of get_debug_msg

    def get_tickers(
            self):
        """get_tickers"""
        return self.tickers
    # end of get_tickers

    def get_balance(
            self):
        """get_balance"""
        return self.balance
    # end of get_balance

    def get_commission(
            self):
        """get_commission"""
        return self.commission
    # end of get_commission

    def get_buys(
            self):
        """get_buys"""
        return self.buys
    # end of get_buys

    def get_sells(
            self):
        """get_sells"""
        return self.sells
    # end of get_sells

    def get_history_dataset(
            self):
        """get_history_dataset"""
        return prepare_history.prepare_history_dataset(
            data=self.create_history_dataset(),
            convert_to_dict=False)
    # end of get_history_dataset

    def get_report_dataset(
            self):
        """get_report_dataset"""
        return prepare_report.prepare_report_dataset(
            data=self.create_report_dataset(),
            convert_to_dict=False)
    # end of get_report_dataset

    def get_owned_shares(
            self,
            ticker):
        """get_owned_shares

        :param ticker: ticker to lookup
        """
        num_owned = 0
        if ticker in self.positions:
            num_owned = self.positions[ticker].get(
                'shares',
                None)
        return num_owned
    # end of get_owned_shares

    def create_buy_order(
            self,
            ticker,
            row,
            minute=None,
            shares=None,
            reason=None,
            orient='records',
            date_format='iso',
            is_live_trading=False):
        """create_buy_order

        create a buy order at the close or ask price

        .. note:: setting the ``minute`` is required to build
            a minute-by-minute ``Trading History``

        :param ticker: string ticker
        :param shares: optional - integer number of shares to buy
            if None buy max number of shares at the ``close`` with the
            available ``balance`` amount.
        :param row: ``dictionary`` or ``pandas.DataFrame``
            row record that will be converted to a
            json-serialized string
        :param minute: optional - string datetime when the order
            minute the order was placed. For ``day`` timeseries
            this is the close of trading (16:00:00 for the day)
            and for ``minute`` timeseries the value will be the
            latest minute from the ``self.df_minute``
            ``pandas.DataFrame``. Normally this value should be
            set to the ``self.use_minute``, and the format is
            ``ae_consts.COMMON_TICK_DATE_FORMAT``
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        :param orient: optional - pandas orient for ``row.to_json()``
        :param date_format: optional - pandas date_format
            parameter for ``row.to_json()``
        :param is_live_trading: optional - bool for filling trades
            for live trading or for backtest tuning filled
            (default ``False`` which is backtest mode)
        """
        close = row['close']
        required_amount_for_a_buy = close + self.commission
        if required_amount_for_a_buy > self.balance:
            if self.verbose_trading:
                log.info(
                    '{} - buy - not enough funds={} < required={} with '
                    'shares={}'.format(
                        self.name,
                        self.balance,
                        required_amount_for_a_buy,
                        self.num_owned))
            return

        dataset_date = row['date']
        use_date = dataset_date
        if minute:
            use_date = minute

        if self.verbose_trading:
            log.info(
                '{} - buy start {} {}@{} - shares={}'.format(
                    self.name,
                    use_date,
                    ticker,
                    close,
                    shares))

        new_buy = None

        order_details = row
        if hasattr(row, 'to_json'):
            order_details = row.to_json(
                orient='records',
                date_format='iso'),

        try:
            num_owned = self.get_owned_shares(
                ticker=ticker)
            new_buy = buy_utils.build_buy_order(
                ticker=ticker,
                close=close,
                num_owned=num_owned,
                shares=shares,
                balance=self.balance,
                commission=self.commission,
                date=dataset_date,
                minute=minute,
                use_key='{}_{}'.format(
                    ticker,
                    dataset_date),
                details=order_details,
                is_live_trading=is_live_trading,
                reason=reason)

            prev_shares = num_owned
            if not prev_shares:
                prev_shares = 0
            prev_bal = ae_consts.to_f(self.balance)
            if new_buy['status'] == ae_consts.TRADE_FILLED:
                if ticker in self.positions:
                    self.positions[ticker]['shares'] = int(
                        new_buy['shares'])
                    self.positions[ticker]['buys'].append(
                        new_buy)
                    (self.num_owned,
                     self.ticker_buys,
                     self.ticker_sells) = self.get_ticker_positions(
                        ticker=ticker)
                    self.created_buy = True
                else:
                    self.positions[ticker] = {
                        'shares': new_buy['shares'],
                        'buys': [
                            new_buy
                        ],
                        'sells': []
                    }
                self.balance = new_buy['balance']
                if self.verbose_trading:
                    log.info(
                        '{} - buy end {} {}@{} {} shares={} cost={} bal={} '
                        'prev_shares={} prev_bal={}'.format(
                            self.name,
                            use_date,
                            ticker,
                            close,
                            ae_consts.get_status(status=new_buy['status']),
                            new_buy['shares'],
                            new_buy['buy_price'],
                            self.balance,
                            prev_shares,
                            prev_bal))
            else:
                if self.verbose_trading:
                    log.info(
                        '{} - buy fail {} {}@{} {} shares={} cost={} '
                        'bal={} '.format(
                            self.name,
                            use_date,
                            ticker,
                            close,
                            ae_consts.get_status(status=new_buy['status']),
                            num_owned,
                            new_buy['buy_price'],
                            self.balance))
            # end of if trade worked or not

            # update the buys
            self.buys.append(new_buy)

            (self.num_owned,
             self.ticker_buys,
             self.ticker_sells) = self.get_ticker_positions(
                ticker=ticker)

            # record the ticker's event if it's a minute timeseries
            if minute:
                self.last_history_dict = self.get_trade_history_node()
                if self.latest_ind_report:
                    ind_configurables = copy.deepcopy(
                        self.latest_ind_report)
                    for ignore_key in self.ind_conf_ignore_keys:
                        ind_configurables.pop(
                            ignore_key,
                            None)
                    self.last_history_dict.update(
                        ind_configurables)

        except Exception as e:
            self.debug_msg = (
                '{} - buy {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of try/ex

    # end of create_buy_order

    def create_sell_order(
            self,
            ticker,
            row,
            minute=None,
            shares=None,
            reason=None,
            orient='records',
            date_format='iso',
            is_live_trading=False):
        """create_sell_order

        create a sell order at the close or ask price

        .. note:: setting the ``minute`` is required to build
            a minute-by-minute ``Trading History``

        :param ticker: string ticker
        :param shares: optional - integer number of shares to sell
            if None sell all owned shares at the ``close``
        :param row: ``pandas.DataFrame`` row record that will
            be converted to a json-serialized string
        :param minute: optional - string datetime when the order
            minute the order was placed. For ``day`` timeseries
            this is the close of trading (16:00:00 for the day)
            and for ``minute`` timeseries the value will be the
            latest minute from the ``self.df_minute``
            ``pandas.DataFrame``. Normally this value should be
            set to the ``self.use_minute``, and the format is
            ``ae_consts.COMMON_TICK_DATE_FORMAT``
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        :param orient: optional - pandas orient for ``row.to_json()``
        :param date_format: optional - pandas date_format
            parameter for ``row.to_json()``
        :param is_live_trading: optional - bool for filling trades
            for live trading or for backtest tuning filled
            (default ``False`` which is backtest mode)
        """
        close = row['close']
        required_amount_for_a_sell = self.commission
        if required_amount_for_a_sell > self.balance:
            if self.verbose_trading:
                log.info(
                    '{} - sell - not enough funds={} < required={} with '
                    'shareds={}'.format(
                        self.name,
                        self.balance,
                        required_amount_for_a_sell,
                        self.num_owned))
            return

        dataset_date = row['date']
        use_date = dataset_date
        if minute:
            use_date = minute

        if self.verbose_trading:
            log.info(
                '{} - sell start {} {}@{}'.format(
                    self.name,
                    use_date,
                    ticker,
                    close))

        new_sell = None
        order_details = row
        if hasattr(row, 'to_json'):
            order_details = row.to_json(
                orient=orient,
                date_format=date_format),

        try:
            num_owned = self.get_owned_shares(
                ticker=ticker)
            new_sell = sell_utils.build_sell_order(
                ticker=ticker,
                close=close,
                num_owned=num_owned,
                shares=shares,
                balance=self.balance,
                commission=self.commission,
                date=dataset_date,
                minute=minute,
                use_key='{}_{}'.format(
                    ticker,
                    dataset_date),
                details=order_details,
                is_live_trading=is_live_trading,
                reason=reason)

            prev_shares = num_owned
            if not prev_shares:
                prev_shares = 0
            prev_bal = ae_consts.to_f(self.balance)
            if new_sell['status'] == ae_consts.TRADE_FILLED:
                if ticker in self.positions:
                    self.positions[ticker]['shares'] = int(
                        new_sell['shares'])
                    self.positions[ticker]['sells'].append(
                        new_sell)
                    (self.num_owned,
                     self.ticker_buys,
                     self.ticker_sells) = self.get_ticker_positions(
                        ticker=ticker)
                    self.created_sell = True
                else:
                    self.positions[ticker] = {
                        'shares': new_sell['shares'],
                        'buys': [],
                        'sells': [
                            new_sell
                        ]
                    }
                self.balance = new_sell['balance']
                if self.verbose_trading:
                    log.info(
                        '{} - sell end {} {}@{} {} shares={} cost={} bal={} '
                        'prev_shares={} prev_bal={}'.format(
                            self.name,
                            use_date,
                            ticker,
                            close,
                            ae_consts.get_status(status=new_sell['status']),
                            num_owned,
                            new_sell['sell_price'],
                            self.balance,
                            prev_shares,
                            prev_bal))
            else:
                if self.verbose_trading:
                    log.info(
                        '{} - sell fail {} {}@{} {} shares={} cost={} '
                        'bal={} '.format(
                            self.name,
                            use_date,
                            ticker,
                            close,
                            ae_consts.get_status(status=new_sell['status']),
                            num_owned,
                            new_sell['sell_price'],
                            self.balance))
            # end of if trade worked or not

            # update the sells
            self.sells.append(new_sell)

            (self.num_owned,
             self.ticker_buys,
             self.ticker_sells) = self.get_ticker_positions(
                ticker=ticker)

            # record the ticker's event if it's a minute timeseries
            if minute:
                self.last_history_dict = self.get_trade_history_node()
                if self.latest_ind_report:
                    ind_configurables = copy.deepcopy(
                        self.latest_ind_report)
                    for ignore_key in self.ind_conf_ignore_keys:
                        ind_configurables.pop(
                            ignore_key,
                            None)
                    self.last_history_dict.update(
                        ind_configurables)

        except Exception as e:
            self.debug_msg = (
                '{} - sell {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of try/ex

    # end of create_sell_order

    def build_progress_label(
            self,
            progress,
            total):
        """build_progress_label

        create a progress label string for the logs

        :param progress: progress counter
        :param total: total number of counts
        """
        percent_done = ae_consts.get_percent_done(
            progress=progress,
            total=total)
        progress_label = '{} {}/{}'.format(
            percent_done,
            progress,
            total)
        return progress_label
    # end of build_progress_label

    def get_supported_tickers_in_data(
            self,
            data):
        """get_supported_tickers_in_data

        For all updates found in ``data`` compare to the
        supported list of ``self.tickers`` to make sure
        the updates are relevant for this algorithm.

        :param data: new data stream to process in this
            algo
        """
        data_for_tickers = []
        for ticker in self.tickers:
            if ticker in data:
                data_for_tickers.append(
                    ticker)
        # end of finding tickers for this algo

        return data_for_tickers
    # end of get_supported_tickers_in_data

    def load_from_dataset(
            self,
            ds_data):
        """load_from_dataset

        Load the member variables from the extracted
        ``ds_data`` dataset.

        algorithms automatically provide the following
        member variables to  ``myalgo.process()`` for
        quickly building algorithms:

        - ``self.df_daily``
        - ``self.df_minute``
        - ``self.df_calls``
        - ``self.df_puts``
        - ``self.df_quote``
        - ``self.df_pricing``
        - ``self.df_stats``
        - ``self.df_peers``
        - ``self.df_iex_news``
        - ``self.df_financials``
        - ``self.df_earnings``
        - ``self.df_dividends``
        - ``self.df_company``
        - ``self.df_yahoo_news``

        .. note:: If a key is not in the dataset, the
            algorithms's member variable will be an empty
            ``pandas.DataFrame([])``. Please ensure the engine
            cached the dataset in redis using a tool like
            ``redis-cli`` to verify the values are in
            memory.

        :param ds_data: extracted, structured
            dataset from redis
        """

        # back up for debugging/tracking/comparing
        self.last_ds_id = self.ds_id
        self.last_ds_date = self.ds_date
        self.last_ds_data = self.ds_data

        # load the new one
        self.ds_data = ds_data

        self.ds_id = self.ds_data.get(
            'id',
            'missing-ID')
        self.ds_date = self.ds_data.get(
            'date',
            'missing-DATE')
        self.ds_data = self.ds_data.get(
            'data',
            'missing-DATA')
        self.df_daily = self.ds_data.get(
            'daily',
            self.empty_pd)
        self.df_minute = self.ds_data.get(
            'minute',
            self.empty_pd)
        self.df_stats = self.ds_data.get(
            'stats',
            self.empty_pd)
        self.df_peers = self.ds_data.get(
            'peers',
            self.empty_pd)
        self.df_financials = self.ds_data.get(
            'financials',
            self.empty_pd)
        self.df_earnings = self.ds_data.get(
            'earnings',
            self.empty_pd)
        self.df_dividends = self.ds_data.get(
            'dividends',
            self.empty_pd)
        self.df_quote = self.ds_data.get(
            'quote',
            self.empty_pd)
        self.df_company = self.ds_data.get(
            'company',
            self.empty_pd)
        self.df_iex_news = self.ds_data.get(
            'news1',
            self.empty_pd)
        self.df_yahoo_news = self.ds_data.get(
            'news',
            self.empty_pd)
        self.df_calls = self.ds_data.get(
            'calls',
            self.empty_pd)
        self.df_puts = self.ds_data.get(
            'puts',
            self.empty_pd)
        self.df_pricing = self.ds_data.get(
            'pricing',
            {})

        self.latest_min = None
        self.backtest_date = self.ds_date
        self.found_minute_data = False

        if not hasattr(self.df_daily, 'index'):
            self.df_daily = self.empty_pd
        if not hasattr(self.df_minute, 'index'):
            self.df_minute = self.empty_pd
        else:
            if 'date' in self.df_minute:
                self.latest_min = self.df_minute['date'].iloc[-1]
                self.found_minute_data = True
        if not hasattr(self.df_stats, 'index'):
            self.df_stats = self.empty_pd
        if not hasattr(self.df_peers, 'index'):
            self.df_peers = self.empty_pd
        if not hasattr(self.df_financials, 'index'):
            self.df_financials = self.empty_pd
        if not hasattr(self.df_earnings, 'index'):
            self.df_earnings = self.empty_pd
        if not hasattr(self.df_dividends, 'index'):
            self.df_dividends = self.empty_pd
        if not hasattr(self.df_quote, 'index'):
            self.df_quote = self.empty_pd
        if not hasattr(self.df_company, 'index'):
            self.df_company = self.empty_pd
        if not hasattr(self.df_iex_news, 'index'):
            self.df_iex_news = self.empty_pd
        if not hasattr(self.df_yahoo_news, 'index'):
            self.df_yahoo_news = self.empty_pd
        if not hasattr(self.df_calls, 'index'):
            self.df_calls = self.empty_pd
        if not hasattr(self.df_puts, 'index'):
            self.df_puts = self.empty_pd
        if not hasattr(self.df_pricing, 'index'):
            self.df_pricing = self.empty_pd

        # set internal values:
        self.trade_date = self.ds_date
        self.created_buy = False
        self.created_sell = False
        self.should_buy = False
        self.should_sell = False

        # by default assume close of trading for the day
        self.use_minute = (
            '{} 16:00:00'.format(
                self.trade_date))

        try:
            if hasattr(self.df_daily, 'index'):
                columns = list(self.df_daily.columns.values)
                if 'high' in columns:
                    self.today_high = float(
                        self.df_daily.iloc[-1]['high'])
                    self.latest_high = self.today_high
                if 'low' in columns:
                    self.today_low = float(
                        self.df_daily.iloc[-1]['low'])
                    self.latest_low = self.today_low
                if 'open' in columns:
                    self.today_open = float(
                        self.df_daily.iloc[-1]['open'])
                    self.latest_open = self.today_open
                if 'close' in columns:
                    self.today_close = float(
                        self.df_daily.iloc[-1]['close'])
                    self.trade_price = self.today_close
                    self.latest_close = self.trade_price
                    if not self.starting_close:
                        self.starting_close = self.today_close
                if 'volume' in columns:
                    self.today_volume = int(
                        self.df_daily.iloc[-1]['volume'])
                    self.latest_volume = self.today_volume
            if hasattr(self.df_minute, 'index'):
                columns = list(self.df_minute.columns.values)
                if 'high' in columns:
                    self.latest_high = float(
                        self.df_minute.iloc[-1]['high'])
                if 'low' in columns:
                    self.latest_low = float(
                        self.df_minute.iloc[-1]['low'])
                if 'open' in columns:
                    self.latest_open = float(
                        self.df_minute.iloc[-1]['open'])
                if 'close' in columns:
                    self.latest_close = float(
                        self.df_minute.iloc[-1]['close'])
                    self.trade_price = self.latest_close
                    if not self.starting_close:
                        self.starting_close = self.latest_close
                if 'volume' in columns:
                    self.latest_volume = int(
                        self.df_minute.iloc[-1]['volume'])
        except Exception as e:
            self.debug_msg = (
                '{} handle - FAILED getting latest prices '
                'for algo={} - ds={} ex={}'.format(
                    self.name,
                    self.ds_id,
                    self.ds_date,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of trying to get the latest prices out of the
        # datasets
    # end of load_from_dataset

    def reset_for_next_run(
            self):
        """reset_for_next_run

        work in progress - clean up all internal member variables
        for another run

        .. note:: random or probablistic predictions may not
            create the same trading history_output_file
        """
        self.debug_msg = ''
        self.loaded_dataset = None
        self.last_history_dict = None
        self.last_handle_data = None
        self.order_history = []
        self.use_minute = None
        self.intraday_start_min = None
        self.intraday_end_min = None
        self.intraday_events = {}
    # end of reset_for_next_run

    def populate_intraday_events_dict(
            self,
            start_min,
            end_min):
        """populate_intraday_events_dict

        For tracking intraday buy/sell/news events with indicators
        use this method to build a dictionary where keys
        are the minutes between ``start_date`` and ``end_date``.
        If both are ``None`` then the ``self.df_minute``

        :param start_min: start datetime for building the
            ``self.intraday_events`` dictionary keys
        :param end_min: end datetime for building the
            ``self.intraday_events`` dictionary keys
        """
        self.intraday_events = {}
        if not self.found_minute_data:
            return

        if end_min < start_min:
            raise Exception(
                'Invalid end_min must be greater than start_min - '
                'self.populate_intraday_events_dict('
                'start_min={}, end_min={}) '
                'algo={}'.format(
                    start_min,
                    end_min,
                    self.name))

        num_minutes = ((end_min - start_min).total_seconds() / 60.0) + 1

        if num_minutes > 1440:
            raise Exception(
                'Invalid number of minutes={} between '
                'start_min={} and end_min={} is more than '
                'the number of minutes in a single day: 1440 '
                'algo={}'.format(
                    num_minutes,
                    start_min,
                    end_min,
                    self.name))

        log.info(
            'num_minutes={} between: {} - {}'.format(
                num_minutes,
                start_min,
                end_min))

        self.intraday_start_min = start_min
        self.intraday_end_min = end_min

        cur_min = start_min
        while cur_min <= end_min:
            min_str = cur_min.strftime(ae_consts.COMMON_TICK_DATE_FORMAT)
            self.intraday_events[min_str] = {}
            for t in self.tickers:
                self.intraday_events[min_str][t] = []
            cur_min += datetime.timedelta(minutes=1)
        # end of while minutes to add to the self.intraday_events dict
    # end of populate_intraday_events_dict

    def record_trade_history_for_dataset(
            self,
            node):
        """record_trade_history_for_dataset

        Build a daily or minute-by-minute trading
        history

        To run an algorithm minute-by-minute set the
        configuration to use:

        .. code-block:: python

            'timeseries': 'minute'

        :param node: cached dataset dictionary node
        """
        # if set to minutes, but this dataset is missing minute-data
        # then record as if it was a daily
        use_day_timeseries = (
            self.timeseries_value == ae_consts.ALGO_TIMESERIES_DAY)
        use_minute_timeseries = (
            self.timeseries_value == ae_consts.ALGO_TIMESERIES_MINUTE)
        if use_day_timeseries or (
                not self.found_minute_data and
                use_minute_timeseries):
            self.use_minute = (
                '{} 16:00:00'.format(
                    self.trade_date))
            self.last_history_dict = self.get_trade_history_node()
            if self.last_history_dict:
                if self.latest_ind_report:
                    ind_configurables = copy.deepcopy(
                        self.latest_ind_report)
                    for ignore_key in self.ind_conf_ignore_keys:
                        ind_configurables.pop(
                            ignore_key,
                            None)
                    self.last_history_dict.update(
                        ind_configurables)
                self.order_history.append(self.last_history_dict)
        # end of if day timeseries
        elif (use_minute_timeseries and self.found_minute_data):
            # add the end of day point to the history
            self.last_history_dict = self.get_trade_history_node()
            if self.last_history_dict:
                if self.latest_ind_report:
                    ind_configurables = copy.deepcopy(
                        self.latest_ind_report)
                    for ignore_key in self.ind_conf_ignore_keys:
                        ind_configurables.pop(
                            ignore_key,
                            None)
                    self.last_history_dict.update(
                        ind_configurables)
                self.order_history.append(self.last_history_dict)
        else:
            raise Exception(
                'Unsupported self.timeseries={} and '
                'self.found_minute_data={} - please use '
                'timeseries=day or timeseries=minute or '
                'timeseries=intraday and ensure the '
                'datasets have \'minute\' data'.format(
                    self.timeseries,
                    self.found_minute_data))
        # end of processing trading history for this dataset
    # end of record_trade_history_for_dataset

    def handle_data(
            self,
            data):
        """handle_data

        process new data for the algorithm using a multi-ticker
        mapping structure

        :param data: dictionary of extracted data from
            the redis pipeline with a structure:
            ::

                ticker = 'SPY'
                # string usually: YYYY-MM-DD
                date = '2018-11-05'
                # redis cache key for the dataset format: <ticker>_<date>
                dataset_id = '{}_{}'.format(
                    ticker,
                    date)
                dataset = {
                    ticker: [
                        {
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
                    ]
                }

        """

        self.debug_msg = (
            '{} handle - start'.format(
                self.name))

        if self.loaded_dataset:
            if self.verbose:
                log.info(
                    '{} handle - using existing dataset '
                    'file={} s3={} redis={}'.format(
                        self.name,
                        self.dsload_output_file,
                        self.dsload_s3_key,
                        self.dsload_redis_key))
            data = self.loaded_dataset

        data_for_tickers = self.get_supported_tickers_in_data(
            data=data)

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            self.debug_msg = (
                '{} handle - tickers={}'.format(
                    self.name,
                    json.dumps(data_for_tickers)))

        for ticker in data_for_tickers:
            num_ticker_datasets = len(data[ticker])
            cur_idx = 1
            for idx, node in enumerate(data[ticker]):
                track_label = self.build_progress_label(
                    progress=cur_idx,
                    total=num_ticker_datasets)
                algo_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                self.debug_msg = (
                    '{} handle - {} - id={} ds={}'.format(
                        self.name,
                        algo_id,
                        node['id'],
                        node['date']))

                valid_run = False
                if self.run_this_date:
                    if node['date'] == self.run_this_date:
                        log.critical(
                            '{} handle - starting at date={} '
                            'with just this dataset: '.format(
                                self.name,
                                node['date']))
                        log.info(
                            '{}'.format(
                                node['data']))
                        valid_run = True
                        self.verbose = True
                        self.verbose_trading = True

                        if self.inspect_dataset:
                            self.view_date_dataset_records(
                                algo_id=algo_id,
                                ticker=ticker,
                                node=node)
                else:
                    valid_run = True

                if valid_run:
                    self.ticker = ticker
                    self.prev_bal = self.balance
                    self.prev_num_owned = self.num_owned

                    (self.num_owned,
                     self.ticker_buys,
                     self.ticker_sells) = self.get_ticker_positions(
                        ticker=ticker)

                    use_daily_timeseries = (
                        self.timeseries_value == ae_consts.ALGO_TIMESERIES_DAY)

                    if use_daily_timeseries:
                        self.handle_daily_dataset(
                            algo_id=algo_id,
                            ticker=ticker,
                            node=node)
                    else:
                        self.handle_minute_dataset(
                            algo_id=algo_id,
                            ticker=ticker,
                            node=node)
                    # end of processing datasets for day vs minute
                # if not debugging a specific dataset in the cache

                if (self.show_balance and
                        (self.num_buys > 0 or self.num_sells > 0)):
                    self.debug_msg = (
                        '{} handle - plot start balance'.format(
                            self.name))
                    self.plot_trading_history_with_balance(
                        algo_id=algo_id,
                        ticker=ticker,
                        node=node)
                    self.debug_msg = (
                        '{} handle - plot done balance'.format(
                            self.name))
                # if showing plots while the algo runs

                cur_idx += 1
        # for all supported tickers

        # store the last handle dataset
        self.last_handle_data = data

        self.debug_msg = (
            '{} handle - end tickers={}'.format(
                self.name,
                num_tickers))

    # end of handle_data

    def handle_daily_dataset(
            self,
            algo_id,
            ticker,
            node):
        """handle_daily_dataset

        handle running the algorithm with daily values

        This method will call ``BaseAlgo.process()`` once per day
        which is also utilizing the daily caching strategy

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param node: dataset to process
        """

        # parse the dataset node and set member variables
        self.debug_msg = (
            '{} START - load dataset id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
        self.load_from_dataset(
            ds_data=node)
        self.debug_msg = (
            '{} END - load dataset id={}'.format(
                ticker,
                node.get('id', 'missing-id')))

        """
        Indicator Processor

        processes the dataset: df_daily
        """
        self.latest_buys = []
        self.latest_sells = []
        if self.iproc:
            self.debug_msg = (
                '{} BASEALGO-START - indicator processing'.format(
                    ticker))
            self.latest_ind_report = self.iproc.process(
                algo_id=algo_id,
                ticker=self.ticker,
                dataset=node)
            self.latest_buys = self.latest_ind_report.get(
                'buys',
                [])
            self.latest_sells = self.latest_ind_report.get(
                'sells',
                [])
            self.debug_msg = (
                '{} BASEALGO-END - indicator processing'.format(
                    ticker))
        # end of indicator processing

        self.num_latest_buys = len(self.latest_buys)
        self.num_latest_sells = len(self.latest_sells)

        """
        Call the Algorithm's process() method
        """
        self.debug_msg = (
            '{} START - process id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
        self.process(
            algo_id=algo_id,
            ticker=self.ticker,
            dataset=node)
        self.debug_msg = (
            '{} END - process id={}'.format(
                ticker,
                node.get('id', 'missing-id')))

        """
        Execute trades based off self.trade_strategy
        """
        self.debug_msg = (
            '{} START - trade id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
        self.trade_off_indicator_buy_and_sell_signals(
            ticker=ticker,
            algo_id=algo_id,
            reason_for_buy=self.buy_reason,
            reason_for_sell=self.sell_reason)
        self.debug_msg = (
            '{} END - trade id={}'.format(
                ticker,
                node.get('id', 'missing-id')))

        """
        Record the Trading History record

        analysis/review using: myalgo.get_result()
        """
        self.debug_msg = (
            '{} START - history id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
        self.record_trade_history_for_dataset(
            node=node)
        self.debug_msg = (
            '{} END - history id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
    # end of handle_daily_dataset

    def prepare_for_new_indicator_run(
            self):
        """prepare_for_new_indicator_run

        Call this for non-daily datasets specifically if the
        algorithm is using ``minute`` timeseries
        """
        self.prev_bal = self.balance
        self.prev_num_owned = self.num_owned
        self.should_buy = False
        self.should_sell = False
        self.num_latest_buys = 0
        self.num_latest_sells = 0
    # end of prepare_for_new_indicator_run

    def handle_minute_dataset(
            self,
            algo_id,
            ticker,
            node):
        """handle_minute_dataset

        handle running the algorithm with daily values

        This method will call ``BaseAlgo.process()`` once per day
        which is also utilizing the daily caching strategy

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param node: dataset to process
        """
        # parse the dataset node and set member variables
        self.debug_msg = (
            '{} START - load dataset id={}'.format(
                ticker,
                node.get('id', 'missing-id')))
        self.load_from_dataset(
            ds_data=node)
        self.debug_msg = (
            '{} END - load dataset id={}'.format(
                ticker,
                node.get('id', 'missing-id')))

        if not self.found_minute_data:
            if self.verbose:
                log.error(
                    'algo={} is missing minute data for day={}'.format(
                        self.name,
                        node.get('date', 'missing date in node={}'.format(
                            node))))
            """
            Record the Trading History record

            analysis/review using: myalgo.get_result()
            """
            self.use_minute = (
                '{} 16:00:00'.format(
                    self.trade_date))
            self.debug_msg = (
                '{} START - saving for missing minute history id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
            self.record_trade_history_for_dataset(
                node=node)
            self.debug_msg = (
                '{} END - for missing history id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
            return

        self.starting_close = None

        num_rows = len(self.df_minute.index)
        for minute_idx, row in self.df_minute.iterrows():

            # map the latest values for the algo to use
            # as if the minute was the latest trading time
            # as it iterates minute-by-minute
            self.latest_min = row.get('date', None)
            self.latest_high = row.get('high', None)
            self.latest_low = row.get('low', None)
            self.latest_open = row.get('open', None)
            self.latest_close = row.get('close', None)
            self.latest_volume = row.get('volume', None)
            self.trade_price = self.latest_close
            self.use_minute = self.latest_min.strftime(
                ae_consts.COMMON_TICK_DATE_FORMAT)

            if not self.starting_close:
                self.starting_close = self.latest_close

            # allow algos to set these custom strings
            # for tracking why a buy and sell happened
            self.buy_reason = None
            self.sell_reason = None

            self.prepare_for_new_indicator_run()

            track_label = self.build_progress_label(
                progress=(minute_idx + 1),
                total=num_rows)
            minute_algo_id = '{} at minute {} - {}'.format(
                algo_id,
                self.latest_min,
                track_label)

            (self.num_owned,
             self.ticker_buys,
             self.ticker_sells) = self.get_ticker_positions(
                ticker=ticker)

            """
            Indicator Processor

            processes the dataset: minute df
            """
            self.latest_buys = []
            self.latest_sells = []
            if self.iproc:
                self.debug_msg = (
                    '{} START - indicator processing '
                    'daily [0-{}]'.format(
                        ticker,
                        (minute_idx + 1)))

                # prune off the minutes that are not the latest
                node['data']['minute'] = self.df_minute.iloc[0:(minute_idx+1)]

                self.latest_ind_report = self.iproc.process(
                    algo_id=minute_algo_id,
                    ticker=self.ticker,
                    dataset=node)
                self.latest_buys = self.latest_ind_report.get(
                    'buys',
                    [])
                self.latest_sells = self.latest_ind_report.get(
                    'sells',
                    [])
                self.debug_msg = (
                    '{} END - indicator processing'.format(
                        ticker))
            # end of indicator processing

            self.num_latest_buys = len(self.latest_buys)
            self.num_latest_sells = len(self.latest_sells)

            if self.inspect_datasets:
                self.inspect_dataset(
                    algo_id=algo_id,
                    ticker=ticker,
                    dataset=node)

            """
            Call the Algorithm's process() method
            """
            self.debug_msg = (
                '{} START - process id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
            self.process(
                algo_id=algo_id,
                ticker=self.ticker,
                dataset=node)
            self.debug_msg = (
                '{} END - process id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))

            """
            Execute trades based off self.trade_strategy
            """
            self.debug_msg = (
                '{} START - trade id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
            self.trade_off_indicator_buy_and_sell_signals(
                ticker=ticker,
                algo_id=algo_id,
                reason_for_buy=self.buy_reason,
                reason_for_sell=self.sell_reason)
            self.debug_msg = (
                '{} END - trade id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))

            """
            Record the Trading History record

            analysis/review using: myalgo.get_result()
            """
            self.debug_msg = (
                '{} START - history id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
            self.record_trade_history_for_dataset(
                node=node)
            self.debug_msg = (
                '{} END - history id={}'.format(
                    ticker,
                    node.get('id', 'missing-id')))
        # end for all rows in the minute dataset
    # end of handle_minute_dataset

    def plot_trading_history_with_balance(
            self,
            algo_id,
            ticker,
            node):
        """

        This will live plot the trading history after each
        day is done

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param node: dataset to process
        """
        trading_history_dict = self.get_history_dataset()
        history_df = trading_history_dict[ticker]
        if not hasattr(history_df, 'to_json'):
            return

        first_date = history_df['date'].iloc[0]
        end_date = history_df['date'].iloc[-1]
        title = (
            'Trading History {} for Algo {}\n'
            'Backtest dates from {} to {}'.format(
                ticker,
                trading_history_dict['algo_name'],
                first_date,
                end_date))
        use_xcol = 'date'
        use_as_date_format = '%d\n%b'
        if self.config_dict['timeseries'] == 'minute':
            use_xcol = 'minute'
            use_as_date_format = '%d %H:%M:%S\n%b'
        xlabel = 'Dates vs {} values'.format(
            trading_history_dict['algo_name'])
        ylabel = 'Algo {}\nvalues'.format(
            trading_history_dict['algo_name'])
        df_filter = (history_df['close'] > 0.01)

        # set default columns:
        red = self.red_column
        blue = self.blue_column
        green = self.green_column
        orange = self.orange_column

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

    # end of plot_trading_history_with_balance

# end of BaseAlgo
