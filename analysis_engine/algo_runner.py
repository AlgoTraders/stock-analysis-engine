"""
A class for running backtests and the latest pricing data
with an automated publishing of the ``Trading History`` to S3
"""

import os
import datetime
import json
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.build_dataset_node as build_dataset_node
import analysis_engine.load_history_dataset as load_history_utils
import analysis_engine.run_custom_algo as run_custom_algo
import analysis_engine.publish as publish
import analysis_engine.algo as base_algo
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class AlgoRunner:
    """AlgoRunner

    Run an algorithm backtest or with the latest
    pricing data and publish the compressed
    trading history to s3 which can be used
    to train AI

    **Full Backtest**

    .. code-block:: python

        import analysis_engine.algo_runner as algo_runner
        runner = algo_runner.AlgoRunner('SPY')
        runner.start()

    **Run Algorithm with Latest Pricing Data**

    .. code-block:: python

        import analysis_engine.algo_runner as algo_runner
        import analysis_engine.plot_trading_history as plot
        ticker = 'SPY'
        runner = algo_runner.AlgoRunner(ticker)
        # run the algorithm with the latest 200 minutes:
        df = runner.latest()
        print(df[['minute', 'close']].tail(5))
        plot.plot_trading_history(
            title=(
                f'{ticker} - ${df["close"].iloc[-1]} '
                f'at: {df["minute"].iloc[-1]}'),
            df=df)

    """

    def __init__(
            self,
            ticker,
            algo_config=None,
            start_date=None,
            end_date=None,
            history_loc=None,
            predictions_loc=None,
            run_on_engine=False,
            verbose_algo=False,
            verbose_processor=False,
            verbose_indicators=False,
            **kwargs):
        """__init__

        constructor

        :param ticker: string ticker
        :param algo_config: optional - string path to file
            (default is ``./cfg/default_algo.json``)
        :param history_loc: optional - string trading history location
            (default is ``s3://algohistory/trade_history_{ticker}``)
        :param predictions_loc: optional - string predictions location
        :param start_date: optional - string start date
        :param end_date: optional - string end date
        :param run_on_engine: optional - bool flag for running local
            or distributed on an engine
            (default is ``False`` - local)
        :param verbose_algo: optional - bool flag for
            debugging the algo
            (default is ``False``)
        :param verbose_processor: optional - bool flag for
            debugging the algo's indicator processor
            (default is ``False``)
        :param verbose_indicators: optional - bool flag for
            debugging the algo's indicators
            (default is ``False``)
        :param kwargs: keyword args dictionary
        """
        self.ticker = None
        if ticker:
            self.ticker = str(ticker).upper()
        self.start_date = start_date
        self.end_date = end_date
        self.start_day = None
        self.end_day = None
        self.run_on_engine = run_on_engine
        self.algo_history_loc = (
            f's3://algohistory/trade_history_{self.ticker}')
        self.algo_predictions_loc = (
            f's3://predictions/{self.ticker}')
        if history_loc:
            self.algo_history_loc = history_loc
        if predictions_loc:
            self.algo_predictions_loc = predictions_loc

        self.pt_s3_access_key = ae_consts.ev(
            'PREDICTIONS_S3_ACCESS_KEY',
            ae_consts.S3_ACCESS_KEY)
        self.pt_s3_secret_key = ae_consts.ev(
            'PREDICTIONS_S3_SECRET_KEY',
            ae_consts.S3_SECRET_KEY)
        self.pt_s3_address = ae_consts.ev(
            'PREDICTIONS_S3_ADDRESS',
            ae_consts.S3_ADDRESS)
        self.pt_s3_secure = str(ae_consts.ev(
            'PREDICTIONS_S3_SECURE',
            ae_consts.S3_SECURE)) == '1'
        self.pt_s3_region = ae_consts.ev(
            'PREDICTIONS_S3_REGION_NAME',
            ae_consts.S3_REGION_NAME)
        self.pt_s3_bucket = self.algo_predictions_loc.split('/')[-2]
        self.pt_s3_key = self.algo_predictions_loc.split('/')[-1]

        self.config_dict = None
        self.use_config_file = algo_config
        if not self.use_config_file:
            if os.path.exists('./cfg/default_algo.json'):
                self.use_config_file = (
                    './cfg/default_algo.json')
            elif os.path.exists('/opt/sa/cfg/default_algo.json'):
                self.use_config_file = (
                    '/opt/sa/cfg/default_algo.json')
            else:
                log.critical(
                    f'Failed: missing algo_config argument pointing to a '
                    f'config file')
                return
        self.config_dict = json.loads(open(self.use_config_file, 'r').read())
        self.algo_mod_path = self.config_dict.get(
            'algo_path',
            ae_consts.ALGO_MODULE_PATH)
        if not os.path.exists(self.algo_mod_path):
            log.critical(
                f'missing algorithm module file from config: '
                f'{self.algo_mod_path}')
            return

        self.balance = 10000.0
        self.commission = 6.0
        self.use_start_date = None
        self.use_end_date = None

        self.inspect_datasets = False
        self.history_json_file = None
        self.run_this_date = None
        self.algo_obj = None
        self.algo_report_loc = None
        self.algo_extract_loc = None
        self.backtest_loc = None
        self.raise_on_err = True

        self.ssl_options = ae_consts.SSL_OPTIONS
        self.transport_options = ae_consts.TRANSPORT_OPTIONS
        self.broker_url = ae_consts.WORKER_BROKER_URL
        self.backend_url = ae_consts.WORKER_BACKEND_URL
        self.path_to_config_module = ae_consts.WORKER_CELERY_CONFIG_MODULE
        self.include_tasks = ae_consts.INCLUDE_TASKS
        self.load_from_s3_bucket = None
        self.load_from_s3_key = None
        self.load_from_redis_key = None
        self.load_from_file = None
        self.load_compress = True
        self.load_publish = True
        self.load_config = None
        self.report_redis_key = None
        self.report_s3_bucket = None
        self.report_s3_key = None
        self.report_file = None
        self.report_compress = True
        self.report_publish = False
        self.report_config = None
        self.history_redis_key = None
        self.history_s3_bucket = None
        self.history_s3_key = None
        self.history_file = None
        self.history_compress = True
        self.history_publish = True
        self.history_config = None
        self.extract_redis_key = None
        self.extract_s3_bucket = None
        self.extract_s3_key = None
        self.extract_file = None
        self.extract_save_dir = None
        self.extract_compress = False
        self.extract_publish = False
        self.extract_config = None
        self.s3_enabled = True
        self.s3_access_key = ae_consts.S3_ACCESS_KEY
        self.s3_secret_key = ae_consts.S3_SECRET_KEY
        self.s3_region_name = ae_consts.S3_REGION_NAME
        self.s3_address = ae_consts.S3_ADDRESS
        self.s3_bucket = ae_consts.S3_BUCKET
        self.s3_key = None
        self.s3_secure = ae_consts.S3_SECURE
        self.redis_enabled = True
        self.redis_address = ae_consts.REDIS_ADDRESS
        self.redis_key = None
        self.redis_password = ae_consts.REDIS_PASSWORD
        self.redis_db = ae_consts.REDIS_DB
        self.redis_expire = ae_consts.REDIS_EXPIRE
        self.redis_serializer = 'json'
        self.redis_encoding = 'utf-8'
        self.publish_to_s3 = True
        self.publish_to_redis = True
        self.publish_to_slack = False
        self.slack_enabled = False
        self.slack_code_block = False
        self.slack_full_width = False

        self.dataset_type = ae_consts.SA_DATASET_TYPE_ALGO_READY
        self.serialize_datasets = ae_consts.DEFAULT_SERIALIZED_DATASETS
        self.compress = False
        self.encoding = 'utf-8'
        self.debug = False
        self.num_rows = 0

        self.auto_fill = True
        self.timeseries = 'minute'
        self.trade_strategy = 'count'
        self.algo_history_s3_bucket = None
        self.algo_history_s3_key = None

        if self.start_date:
            self.use_start_date = f'{str(self.start_date)} 00:00:00'
            datetime.datetime.strptime(
                self.start_date,
                ae_consts.COMMON_DATE_FORMAT)
        if self.end_date:
            self.use_end_date = f'{str(self.end_date)} 00:00:00'
            datetime.datetime.strptime(
                self.end_date,
                ae_consts.COMMON_DATE_FORMAT)

        """
        Finalize the algo config
        """
        self.debug = False
        self.verbose_algo = verbose_algo
        self.verbose_processor = verbose_processor
        self.verbose_indicators = verbose_indicators

        if self.config_dict:
            if self.ticker:
                self.config_dict['ticker'] = self.ticker
            else:
                self.ticker = (
                    str(self.config_dict['ticker']).upper())
            self.config_dict['balance'] = self.balance
            self.config_dict['commission'] = self.commission

        if self.verbose_algo:
            self.config_dict['verbose'] = self.verbose_algo
        if self.verbose_processor:
            self.config_dict['verbose_processor'] = self.verbose_processor
        if self.verbose_indicators:
            self.config_dict['verbose_indicators'] = self.verbose_indicators
        if self.inspect_datasets:
            self.config_dict['inspect_datasets'] = self.inspect_datasets
        if self.run_this_date:
            self.config_dict['run_this_date'] = self.run_this_date

        if self.backtest_loc:
            if 's3://' in self.backtest_loc:
                self.load_from_s3_bucket = self.backtest_loc.split('/')[-2]
                self.load_from_s3_key = self.backtest_loc.split('/')[-1]
            elif 'redis://' in self.backtest_loc:
                self.load_from_redis_key = self.backtest_loc.split('/')[-1]
            elif 'file:/' in self.backtest_loc:
                self.load_from_file = self.backtest_loc.split(':')[-1]
            else:
                log.error(
                    'invalid -b <backtest dataset file> specified. '
                    f'{self.backtest_loc} '
                    'please use either: '
                    '-b file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-b s3://algoready/SPY-latest.json or '
                    '-b redis://SPY-latest')
            self.load_publish = True

        if self.algo_history_loc:
            if 's3://' in self.algo_history_loc:
                self.history_s3_bucket = self.algo_history_loc.split('/')[-2]
                self.history_s3_key = self.algo_history_loc.split('/')[-1]
            elif 'redis://' in self.algo_history_loc:
                self.history_redis_key = self.algo_history_loc.split('/')[-1]
            elif 'file:/' in self.algo_history_loc:
                self.history_file = self.algo_history_loc.split(':')[-1]
            else:
                log.error(
                    'invalid -p <backtest dataset file> specified. '
                    f'{self.algo_history_loc} '
                    'please use either: '
                    '-p file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-p s3://algoready/SPY-latest.json or '
                    '-p redis://SPY-latest')
            self.history_publish = True

        if self.algo_report_loc:
            if 's3://' in self.algo_report_loc:
                self.report_s3_bucket = self.algo_report_loc.split('/')[-2]
                self.report_s3_key = self.algo_report_loc.split('/')[-1]
            elif 'redis://' in self.algo_report_loc:
                self.report_redis_key = self.algo_report_loc.split('/')[-1]
            elif 'file:/' in self.algo_report_loc:
                self.report_file = self.algo_report_loc.split(':')[-1]
            else:
                log.error(
                    'invalid -o <backtest dataset file> specified. '
                    f'{self.algo_report_loc} '
                    'please use either: '
                    '-o file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-o s3://algoready/SPY-latest.json or '
                    '-o redis://SPY-latest')
            self.report_publish = True

        if self.algo_extract_loc:
            if 's3://' in self.algo_extract_loc:
                self.extract_s3_bucket = self.algo_extract_loc.split('/')[-2]
                self.extract_s3_key = self.algo_extract_loc.split('/')[-1]
            elif 'redis://' in self.algo_extract_loc:
                self.extract_redis_key = self.algo_extract_loc.split('/')[-1]
            elif 'file:/' in self.algo_extract_loc:
                self.extract_file = self.algo_extract_loc.split(':')[-1]
            else:
                log.error(
                    'invalid -e <backtest dataset file> specified. '
                    f'{self.algo_extract_loc} '
                    'please use either: '
                    '-e file:/opt/sa/tests/datasets/algo/SPY-latest.json or '
                    '-e s3://algoready/SPY-latest.json or '
                    '-e redis://SPY-latest')
            self.extract_publish = True

        self.use_name = self.config_dict.get(
            'name',
            'missing-algo-name')
        self.auto_fill = self.config_dict.get(
            'auto_fill',
            self.auto_fill)
        self.timeseries = self.config_dict.get(
            'timeseries',
            self.timeseries)
        self.trade_strategy = self.config_dict.get(
            'trade_strategy',
            self.trade_strategy)

        self.iex_datasets = ae_consts.IEX_DATASETS_DEFAULT
        self.common_fetch_vals = {}
        self.common_fetch_vals['ticker'] = self.ticker
        self.common_fetch_vals['celery_disabled'] = True
        self.common_fetch_vals['label'] = 'lp'
        self.common_fetch_vals['iex_datasets'] = self.iex_datasets
        self.common_fetch_vals['s3_enabled'] = False
        self.common_fetch_vals['s3_address'] = None
        self.common_fetch_vals['s3_bucket'] = None
        self.common_fetch_vals['s3_key'] = None
        self.common_fetch_vals['s3_access_key'] = None
        self.common_fetch_vals['s3_secret_key'] = None
        self.common_fetch_vals['s3_region_name'] = None
        self.common_fetch_vals['s3_secure'] = None
        self.common_fetch_vals['redis_enabled'] = True
        self.common_fetch_vals['redis_address'] = self.redis_address
        self.common_fetch_vals['redis_password'] = self.redis_password
        self.common_fetch_vals['redis_expire'] = None
        self.common_fetch_vals['redis_db'] = self.redis_db

        self.history_df = None
        self.slack_enabled = False
    # end of __init__

    def start(
            self):
        """start

        Start the algorithm backtest
        """

        log.info(
            'starting algo '
            f's3://{self.history_s3_bucket}/{self.history_s3_key}')

        self.algo_res = run_custom_algo.run_custom_algo(
            mod_path=self.algo_mod_path,
            ticker=self.config_dict['ticker'],
            balance=self.config_dict['balance'],
            commission=self.config_dict['commission'],
            name=self.use_name,
            start_date=self.use_start_date,
            end_date=self.use_end_date,
            auto_fill=self.auto_fill,
            config_dict=self.config_dict,
            load_from_s3_bucket=self.load_from_s3_bucket,
            load_from_s3_key=self.load_from_s3_key,
            load_from_redis_key=self.load_from_redis_key,
            load_from_file=self.load_from_file,
            load_compress=self.load_compress,
            load_publish=self.load_publish,
            load_config=self.load_config,
            report_redis_key=self.report_redis_key,
            report_s3_bucket=self.report_s3_bucket,
            report_s3_key=self.report_s3_key,
            report_file=self.report_file,
            report_compress=self.report_compress,
            report_publish=self.report_publish,
            report_config=self.report_config,
            history_redis_key=self.history_redis_key,
            history_s3_bucket=self.history_s3_bucket,
            history_s3_key=self.history_s3_key,
            history_file=self.history_file,
            history_compress=self.history_compress,
            history_publish=self.history_publish,
            history_config=self.history_config,
            extract_redis_key=self.extract_redis_key,
            extract_s3_bucket=self.extract_s3_bucket,
            extract_s3_key=self.extract_s3_key,
            extract_file=self.extract_file,
            extract_save_dir=self.extract_save_dir,
            extract_compress=self.extract_compress,
            extract_publish=self.extract_publish,
            extract_config=self.extract_config,
            publish_to_slack=self.publish_to_slack,
            publish_to_s3=self.publish_to_s3,
            publish_to_redis=self.publish_to_redis,
            dataset_type=self.dataset_type,
            serialize_datasets=self.serialize_datasets,
            compress=self.compress,
            encoding=self.encoding,
            redis_enabled=self.redis_enabled,
            redis_key=self.redis_key,
            redis_address=self.redis_address,
            redis_db=self.redis_db,
            redis_password=self.redis_password,
            redis_expire=self.redis_expire,
            redis_serializer=self.redis_serializer,
            redis_encoding=self.redis_encoding,
            s3_enabled=self.s3_enabled,
            s3_key=self.s3_key,
            s3_address=self.s3_address,
            s3_bucket=self.s3_bucket,
            s3_access_key=self.s3_access_key,
            s3_secret_key=self.s3_secret_key,
            s3_region_name=self.s3_region_name,
            s3_secure=self.s3_secure,
            slack_enabled=self.slack_enabled,
            slack_code_block=self.slack_code_block,
            slack_full_width=self.slack_full_width,
            dataset_publish_extract=self.extract_publish,
            dataset_publish_history=self.history_publish,
            dataset_publish_report=self.report_publish,
            run_on_engine=self.run_on_engine,
            auth_url=self.broker_url,
            backend_url=self.backend_url,
            include_tasks=self.include_tasks,
            ssl_options=self.ssl_options,
            transport_options=self.transport_options,
            path_to_config_module=self.path_to_config_module,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            verbose=self.verbose_algo,
            raise_on_err=self.raise_on_err)

        self.wait_for_algo_to_finish()
    # end of start

    def wait_for_algo_to_finish(
            self):
        """wait_for_algo_to_finish

        wait until the algorithm finishes
        """

        self.algo_history_s3_bucket = None
        self.algo_history_s3_key = None
        self.task_id = None
        if self.run_on_engine:
            self.task_id = self.algo_res.get(
                'rec', {}).get('task_id', None)
        if self.task_id:
            log.info(
                f'waiting - algo task_id={self.task_id} to finish')
            res = self.task_id.get()
            history_config = res.get(
                'algo_req', {}).get(
                    'history_config', None)
            self.algo_history_s3_bucket = history_config.get(
                's3_bucket', None)
            self.algo_history_s3_key = history_config.get(
                's3_key', None)
            self.load_trading_history()
        else:
            history_records = self.algo_res.get(
                'rec', {}).get(
                    'history', None)
            self.algo_history_s3_bucket = self.history_s3_bucket
            self.algo_history_s3_key = self.history_s3_key
            self.history_df = pd.DataFrame(history_records)
            self.determine_latest_times_in_history()

        self.num_rows = len(self.history_df.index)

        log.info(
            f'loaded history rows={self.num_rows} '
            f'dates={self.start_date} to {self.end_date}')
    # end of wait_for_algo_to_finish

    def determine_latest_times_in_history(
            self):
        """determine_latest_times_in_history

        determine the latest minute or day in the pricing dataset
        and convert ``date`` and ``minute`` columns to ``datetime``
        objects
        """
        self.history_df['date'] = pd.to_datetime(
            self.history_df['date'])
        self.start_day = self.history_df['date'].iloc[0]
        self.end_day = self.history_df['date'].iloc[-1]
        self.start_date = self.history_df['date'].iloc[0]
        self.end_date = self.history_df['date'].iloc[-1]
        if 'minute' in self.history_df:
            self.history_df['minute'] = pd.to_datetime(
                self.history_df['minute'])
            self.start_date = self.history_df['minute'].iloc[0]
            self.end_date = self.history_df['minute'].iloc[-1]
    # end of determine_latest_times_in_history

    def load_trading_history(
            self,
            s3_access_key=None,
            s3_secret_key=None,
            s3_address=None,
            s3_region=None,
            s3_bucket=None,
            s3_key=None,
            s3_secure=ae_consts.NOT_SET,
            **kwargs):
        """load_trading_history

        Helper for loading an algorithm ``Trading History`` from
        S3

        :param s3_access_key: access key
        :param s3_secret_key: secret
        :param s3_address: address
        :param s3_region: region
        :param s3_bucket: bucket
        :param s3_key: key
        :param s3_secure: secure flag
        :param kwargs: support for keyword arg dict
        """
        use_s3_access_key = self.s3_access_key
        use_s3_secret_key = self.s3_secret_key
        use_s3_address = self.s3_address
        use_s3_region = self.s3_region_name
        use_s3_bucket = self.s3_bucket
        use_s3_key = self.s3_key
        use_s3_secure = self.s3_secure

        if s3_access_key:
            use_s3_access_key = s3_access_key
        if s3_secret_key:
            use_s3_secret_key = s3_secret_key
        if s3_address:
            use_s3_address = s3_address
        if s3_region:
            use_s3_region = s3_region
        if s3_bucket:
            use_s3_bucket = s3_bucket
        if s3_key:
            use_s3_key = s3_key
        if s3_secure != ae_consts.NOT_SET:
            use_s3_secure = s3_secure

        if s3_key and s3_bucket:
            log.info(
                f'using - td s3://{use_s3_address}/'
                f'{use_s3_bucket}/{use_s3_key}')
        else:
            log.info(
                f'load - td s3://{use_s3_address}/'
                f'{use_s3_bucket}/{use_s3_key}')

        load_res = load_history_utils.load_history_dataset(
            s3_access_key=use_s3_access_key,
            s3_secret_key=use_s3_secret_key,
            s3_address=use_s3_address,
            s3_region_name=use_s3_region,
            s3_bucket=use_s3_bucket,
            s3_key=use_s3_key,
            s3_secure=use_s3_secure)

        if self.ticker not in load_res:
            log.critical(
                'failed to load history: '
                f's3://{self.s3_bucket}/{self.s3_key}')
            self.history_df = None
            return

        self.history_df = load_res[self.ticker]
        self.determine_latest_times_in_history()

        log.info(
            f'found - td s3://{use_s3_address}/'
            f'{use_s3_bucket}/{use_s3_key} '
            f'rows={len(self.history_df.index)}')
    # end of load_trading_history

    def get_history(
            self):
        """get_history"""
        return self.history_df
    # end of get_history

    def get_latest_day(
            self):
        """get_latest_day"""
        if 'date' in self.history_df:
            return self.end_day
        else:
            return None
    # end of get_latest_day

    def get_latest_minute(
            self):
        """get_latest_minute"""
        if 'minute' in self.history_df:
            return self.end_date
        else:
            return None
    # end of get_latest_minute

    def publish_trading_history(
            self,
            records_for_history,
            pt_s3_access_key=None,
            pt_s3_secret_key=None,
            pt_s3_address=None,
            pt_s3_region=None,
            pt_s3_bucket=None,
            pt_s3_key=None,
            pt_s3_secure=ae_consts.NOT_SET,
            **kwargs):
        """publish_trading_history

        Helper for publishing a trading history
        to another S3 service like AWS

        :param records_for_history: list of dictionaries
            for the history file
        :param pt_s3_access_key: access key
        :param pt_s3_secret_key: secret
        :param pt_s3_address: address
        :param pt_s3_region: region
        :param pt_s3_bucket: bucket
        :param pt_s3_key: key
        :param pt_s3_secure: secure flag
        :param kwargs: support for keyword arg dict
        """
        use_s3_access_key = self.pt_s3_access_key
        use_s3_secret_key = self.pt_s3_secret_key
        use_s3_address = self.pt_s3_address
        use_s3_region = self.pt_s3_region
        use_s3_bucket = self.pt_s3_bucket
        use_s3_key = self.pt_s3_key
        use_s3_secure = self.pt_s3_secure

        use_s3_enabled = kwargs.get(
            's3_enabled', True)
        use_redis_enabled = kwargs.get(
            'redis_enabled', False)
        use_redis_address = kwargs.get(
            'redis_address', None)
        use_redis_db = kwargs.get(
            'redis_db', None)
        use_redis_key = kwargs.get(
            'redis_key', None)
        use_redis_password = kwargs.get(
            'redis_password', None)
        use_redis_expire = kwargs.get(
            'redis_expire', None)
        use_redis_serializer = kwargs.get(
            'redis_serializer', 'json')
        use_redis_encoding = kwargs.get(
            'redis_encoding', 'utf-8')
        verbose = kwargs.get(
            'verbose', False)

        if pt_s3_access_key:
            use_s3_access_key = pt_s3_access_key
        if pt_s3_secret_key:
            use_s3_secret_key = pt_s3_secret_key
        if pt_s3_address:
            use_s3_address = pt_s3_address
        if pt_s3_region:
            use_s3_region = pt_s3_region
        if pt_s3_bucket:
            use_s3_bucket = pt_s3_bucket
        if pt_s3_key:
            use_s3_key = pt_s3_key
        if pt_s3_secure != ae_consts.NOT_SET:
            use_s3_secure = pt_s3_secure

        rec = {
            'tickers': self.ticker,
            'version': int(ae_consts.ALGO_HISTORY_VERSION),
            'last_trade_date': ae_utils.get_last_close_str(),
            'algo_config_dict': self.config_dict,
            'algo_name':  self.use_name,
            'created': ae_utils.utc_now_str(),
            self.ticker: records_for_history
        }

        num_bytes = len(str(rec))
        num_mb = ae_consts.get_mb(num_bytes)

        msg = (
            f'publish - {self.ticker} - {rec["last_trade_date"]} '
            # f'{use_s3_access_key} with: {use_s3_secret_key} '
            f's3_loc={use_s3_address}/{use_s3_bucket}/{use_s3_key} '
            f'mb={num_mb}MB')
        log.info(msg)

        publish.publish(
            data=rec,
            label='pub',
            df_compress=True,
            compress=False,
            convert_to_dict=False,
            output_file=None,
            redis_enabled=use_redis_enabled,
            redis_key=use_redis_key,
            redis_address=use_redis_address,
            redis_db=use_redis_db,
            redis_password=use_redis_password,
            redis_expire=use_redis_expire,
            redis_serializer=use_redis_serializer,
            redis_encoding=use_redis_encoding,
            s3_enabled=use_s3_enabled,
            s3_key=use_s3_key,
            s3_address=use_s3_address,
            s3_bucket=use_s3_bucket,
            s3_access_key=use_s3_access_key,
            s3_secret_key=use_s3_secret_key,
            s3_region_name=use_s3_region,
            s3_secure=use_s3_secure,
            slack_enabled=False,
            verbose=verbose)
    # end of publish_trading_history

    def latest(
            self,
            date_str=None,
            start_row=-200,
            extract_iex=True,
            extract_yahoo=False,
            extract_td=True,
            verbose=False,
            **kwargs):
        """latest

        Run the algorithm with the latest pricing data. Also
        supports running a backtest for a historical date in
        the pricing history (format ``YYYY-MM-DD``)

        :param date_str: optional - string start date ``YYYY-MM-DD``
            default is the latest close date
        :param start_row: negative number of rows back
            from the end of the list in the data
            default is ``-200`` where this means the algorithm
            will process the latest 200 rows in the minute
            dataset
        :param extract_iex: bool flag for extracting from ``IEX``
        :param extract_yahoo: bool flag for extracting from ``Yahoo``
            which is disabled as of 1/2019
        :param extract_td: bool flag for extracting from ``Tradier``
        :param verbose: bool flag for logs
        :param kwargs: keyword arg dict
        """
        use_date_str = date_str
        if not use_date_str:
            use_date_str = ae_utils.get_last_close_str()

        log.info(
            f'creating algo')
        self.algo_obj = base_algo.BaseAlgo(
            ticker=self.config_dict['ticker'],
            balance=self.config_dict['balance'],
            commission=self.config_dict['commission'],
            name=self.use_name,
            start_date=self.use_start_date,
            end_date=self.use_end_date,
            auto_fill=self.auto_fill,
            config_dict=self.config_dict,
            load_from_s3_bucket=self.load_from_s3_bucket,
            load_from_s3_key=self.load_from_s3_key,
            load_from_redis_key=self.load_from_redis_key,
            load_from_file=self.load_from_file,
            load_compress=self.load_compress,
            load_publish=self.load_publish,
            load_config=self.load_config,
            report_redis_key=self.report_redis_key,
            report_s3_bucket=self.report_s3_bucket,
            report_s3_key=self.report_s3_key,
            report_file=self.report_file,
            report_compress=self.report_compress,
            report_publish=self.report_publish,
            report_config=self.report_config,
            history_redis_key=self.history_redis_key,
            history_s3_bucket=self.history_s3_bucket,
            history_s3_key=self.history_s3_key,
            history_file=self.history_file,
            history_compress=self.history_compress,
            history_publish=self.history_publish,
            history_config=self.history_config,
            extract_redis_key=self.extract_redis_key,
            extract_s3_bucket=self.extract_s3_bucket,
            extract_s3_key=self.extract_s3_key,
            extract_file=self.extract_file,
            extract_save_dir=self.extract_save_dir,
            extract_compress=self.extract_compress,
            extract_publish=self.extract_publish,
            extract_config=self.extract_config,
            publish_to_slack=self.publish_to_slack,
            publish_to_s3=self.publish_to_s3,
            publish_to_redis=self.publish_to_redis,
            dataset_type=self.dataset_type,
            serialize_datasets=self.serialize_datasets,
            compress=self.compress,
            encoding=self.encoding,
            redis_enabled=self.redis_enabled,
            redis_key=self.redis_key,
            redis_address=self.redis_address,
            redis_db=self.redis_db,
            redis_password=self.redis_password,
            redis_expire=self.redis_expire,
            redis_serializer=self.redis_serializer,
            redis_encoding=self.redis_encoding,
            s3_enabled=self.s3_enabled,
            s3_key=self.s3_key,
            s3_address=self.s3_address,
            s3_bucket=self.s3_bucket,
            s3_access_key=self.s3_access_key,
            s3_secret_key=self.s3_secret_key,
            s3_region_name=self.s3_region_name,
            s3_secure=self.s3_secure,
            slack_enabled=self.slack_enabled,
            slack_code_block=self.slack_code_block,
            slack_full_width=self.slack_full_width,
            dataset_publish_extract=self.extract_publish,
            dataset_publish_history=self.history_publish,
            dataset_publish_report=self.report_publish,
            run_on_engine=self.run_on_engine,
            auth_url=self.broker_url,
            backend_url=self.backend_url,
            include_tasks=self.include_tasks,
            ssl_options=self.ssl_options,
            transport_options=self.transport_options,
            path_to_config_module=self.path_to_config_module,
            timeseries=self.timeseries,
            trade_strategy=self.trade_strategy,
            verbose=False,
            raise_on_err=self.raise_on_err)

        log.info(
            f'run latest - start')

        ticker = self.config_dict['ticker']
        dataset_id = f'{ticker}_{use_date_str}'
        self.common_fetch_vals['base_key'] = dataset_id
        verbose_extract = self.config_dict.get('verbose_extract', False)
        indicator_datasets = self.algo_obj.get_indicator_datasets()
        ticker_data = build_dataset_node.build_dataset_node(
            ticker=ticker,
            date=use_date_str,
            datasets=indicator_datasets,
            service_dict=self.common_fetch_vals,
            verbose=verbose_extract)

        algo_data_req = {
            ticker: [
                {
                    'id': dataset_id,  # id is currently the cache key in redis
                    'date': use_date_str,  # used to confirm dates in asc order
                    'data': ticker_data,
                    'start_row': start_row
                }
            ]
        }

        if verbose:
            log.info(
                f'extract - {dataset_id} '
                f'dataset={len(algo_data_req[ticker])}')

        # this could be a separate celery task
        try:
            if verbose:
                log.info(
                    f'handle_data START - {dataset_id}')
            self.algo_obj.handle_data(
                data=algo_data_req)
            if verbose:
                log.info(
                    f'handle_data END - {dataset_id}')
        except Exception as e:
            a_name = self.algo_obj.get_name()
            a_debug_msg = self.algo_obj.get_debug_msg()
            if not a_debug_msg:
                a_debug_msg = 'debug message not set'
            # a_config_dict = ae_consts.ppj(self.algo_obj.config_dict)
            msg = (
                f'{dataset_id} - algo={a_name} '
                f'encountered exception in handle_data tickers={ticker} '
                f'from ex={e} '
                f'and failed during operation: {a_debug_msg}')
            log.critical(f'{msg}')
        # end try/ex

        log.info('run latest - create history')

        history_ds = self.algo_obj.create_history_dataset()
        self.history_df = pd.DataFrame(history_ds[ticker])
        self.determine_latest_times_in_history()

        self.num_rows = len(self.history_df.index)

        if verbose:
            log.info(self.history_df[['minute', 'close']].tail(5))

        log.info(
            f'run latest minute={self.end_date} - '
            f'rows={self.num_rows} - done')

        return self.get_history()
    # end of latest

# end of AlgoRunner
