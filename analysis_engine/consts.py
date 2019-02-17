"""
Consts and helper functions

**Algorithm Environment Variables**

.. code-block:: python

    ALGO_MODULE_PATH = ev(
        'ALGO_MODULE_PATH',
        '/opt/sa/analysis_engine/mocks/example_algo_minute.py')
    ALGO_BASE_MODULE_PATH = ev(
        'ALGO_BASE_MODULE_PATH',
        '/opt/sa/analysis_engine/algo.py')
    ALGO_MODULE_NAME = ev(
        'ALGO_MODULE_NAME',
        'example_algo_minute')
    ALGO_VERSION = ev(
        'ALGO_VERSION',
        '1')
    ALGO_BUYS_S3_BUCKET_NAME = ev(
        'ALGO_BUYS_S3_BUCKET_NAME',
        'algobuys')
    ALGO_SELLS_S3_BUCKET_NAME = ev(
        'ALGO_SELLS_S3_BUCKET_NAME',
        'algosells')
    ALGO_RESULT_S3_BUCKET_NAME = ev(
        'ALGO_RESULT_S3_BUCKET_NAME',
        'algoresults')
    ALGO_READY_DATASET_S3_BUCKET_NAME = ev(
        'ALGO_READY_DATASET_S3_BUCKET_NAME',
        'algoready')
    ALGO_EXTRACT_DATASET_S3_BUCKET_NAME = ev(
        'ALGO_EXTRACT_DATASET_S3_BUCKET_NAME',
        'algoready')
    ALGO_HISTORY_DATASET_S3_BUCKET_NAME = ev(
        'ALGO_HISTORY_DATASET_S3_BUCKET_NAME',
        'algohistory')
    ALGO_REPORT_DATASET_S3_BUCKET_NAME = ev(
        'ALGO_REPORT_DATASET_S3_BUCKET_NAME',
        'algoreport')
    ALGO_BACKUP_DATASET_S3_BUCKET_NAME = ev(
        'ALGO_BACKUP_DATASET_S3_BUCKET_NAME',
        'algobackup')
    ALGO_READY_DIR = ev(
        'ALGO_READY_DIR',
        '/tmp')
    ALGO_EXTRACT_DIR = ev(
        'ALGO_EXTRACT_DIR',
        '/tmp')
    ALGO_HISTORY_DIR = ev(
        'ALGO_HISTORY_HISTORY_DIR',
        '/tmp')
    ALGO_REPORT_DIR = ev(
        'ALGO_REPORT_DIR',
        '/tmp')
    ALGO_LOAD_DIR = ev(
        'ALGO_LOAD_DIR',
        '/tmp')
    ALGO_BACKUP_DIR = ev(
        'ALGO_BACKUP_DIR',
        '/tmp')
    ALGO_READY_REDIS_ADDRESS = ev(
        'ALGO_READY_REDIS_ADDRESS',
        'localhost:6379')
    ALGO_EXTRACT_REDIS_ADDRESS = ev(
        'ALGO_EXTRACT_REDIS_ADDRESS',
        'localhost:6379')
    ALGO_HISTORY_REDIS_ADDRESS = ev(
        'ALGO_HISTORY_REDIS_ADDRESS',
        'localhost:6379')
    ALGO_REPORT_REDIS_ADDRESS = ev(
        'ALGO_REPORT_REDIS_ADDRESS',
        'localhost:6379')
    ALGO_BACKUP_REDIS_ADDRESS = ev(
        'ALGO_BACKUP_REDIS_ADDRESS',
        'localhost:6379')
    ALGO_HISTORY_VERSION = ev(
        'ALGO_HISTORY_VERSION',
        '1')
    ALGO_REPORT_VERSION = ev(
        'ALGO_REPORT_VERSION',
        '1')

**Stock and Analysis Environment Variables**

::

    TICKER = ev(
        'TICKER',
        'SPY')
    TICKER_ID = int(ev(
        'TICKER_ID',
        '1'))
    DEFAULT_TICKERS = ev(
        'DEFAULT_TICKERS',
        'SPY,AMZN,TSLA,NFLX').split(',')
    NEXT_EXP = opt_dates.option_expiration()
    NEXT_EXP_STR = NEXT_EXP.strftime('%Y-%m-%d')

**Logging Environment Variables**

.. code-block:: python

    LOG_CONFIG_PATH = ev(
        'LOG_CONFIG_PATH',
        './analysis_engine/log/logging.json')

**Slack Environment Variables**

.. code-block:: python

    SLACK_WEBHOOK = ev(
        'SLACK_WEBHOOK',
        None)
    SLACK_ACCESS_TOKEN = ev(
        'SLACK_ACCESS_TOKEN',
        None
    )
    SLACK_PUBLISH_PLOT_CHANNELS = ev(
        'SLACK_PUBLISH_PLOT_CHANNELS',
        None
    )
    PROD_SLACK_ALERTS = ev(
        'PROD_SLACK_ALERTS',
        '0')

**Celery Environment Variables**

.. code-block:: python

    SSL_OPTIONS = {}
    TRANSPORT_OPTIONS = {}
    WORKER_BROKER_URL = ev(
        'WORKER_BROKER_URL',
        'redis://localhost:6379/11')
    WORKER_BACKEND_URL = ev(
        'WORKER_BACKEND_URL',
        'redis://localhost:6379/12')
    WORKER_CELERY_CONFIG_MODULE = ev(
        'WORKER_CELERY_CONFIG_MODULE',
        'analysis_engine.work_tasks.celery_config')
    WORKER_TASKS = ev(
        'WORKER_TASKS',
        ('analysis_engine.work_tasks.task_run_algo'))
    INCLUDE_TASKS = WORKER_TASKS.split(',')

**Supported S3 Environment Variables**

.. code-block:: python

    ENABLED_S3_UPLOAD = ev(
        'ENABLED_S3_UPLOAD',
        '0') == '1'
    S3_ACCESS_KEY = ev(
        'AWS_ACCESS_KEY_ID',
        'trexaccesskey')
    S3_SECRET_KEY = ev(
        'AWS_SECRET_ACCESS_KEY',
        'trex123321')
    S3_REGION_NAME = ev(
        'AWS_DEFAULT_REGION',
        'us-east-1')
    S3_ADDRESS = ev(
        'S3_ADDRESS',
        '0.0.0.0:9000')
    S3_SECURE = ev(
        'S3_SECURE',
        '0') == '1'
    S3_BUCKET = ev(
        'S3_BUCKET',
        'pricing')
    S3_COMPILED_BUCKET = ev(
        'S3_COMPILED_BUCKET',
        'compileddatasets')
    S3_KEY = ev(
        'S3_KEY',
        'test_key')
    DAILY_S3_BUCKET_NAME = ev(
        'DAILY_S3_BUCKET_NAME',
        'daily')
    MINUTE_S3_BUCKET_NAME = ev(
        'MINUTE_S3_BUCKET_NAME',
        'minute')
    QUOTE_S3_BUCKET_NAME = ev(
        'QUOTE_S3_BUCKET_NAME',
        'quote')
    STATS_S3_BUCKET_NAME = ev(
        'STATS_S3_BUCKET_NAME',
        'stats')
    PEERS_S3_BUCKET_NAME = ev(
        'PEERS_S3_BUCKET_NAME',
        'peers')
    NEWS_S3_BUCKET_NAME = ev(
        'NEWS_S3_BUCKET_NAME',
        'news')
    FINANCIALS_S3_BUCKET_NAME = ev(
        'FINANCIALS_S3_BUCKET_NAME',
        'financials')
    EARNINGS_S3_BUCKET_NAME = ev(
        'EARNINGS_S3_BUCKET_NAME',
        'earnings')
    DIVIDENDS_S3_BUCKET_NAME = ev(
        'DIVIDENDS_S3_BUCKET_NAME',
        'dividends')
    COMPANY_S3_BUCKET_NAME = ev(
        'COMPANY_S3_BUCKET_NAME',
        'company')
    PREPARE_S3_BUCKET_NAME = ev(
        'PREPARE_S3_BUCKET_NAME',
        'prepared')
    ANALYZE_S3_BUCKET_NAME = ev(
        'ANALYZE_S3_BUCKET_NAME',
        'analyzed')
    SCREENER_S3_BUCKET_NAME = ev(
        'SCREENER_S3_BUCKET_NAME',
        'screener-data')
    PRICING_S3_BUCKET_NAME = ev(
        'PRICING_S3_BUCKET_NAME',
        'pricing')
    OPTIONS_S3_BUCKET_NAME = ev(
        'OPTIONS_S3_BUCKET_NAME',
        'options')

**Supported Redis Environment Variables**

.. code-block:: python

    ENABLED_REDIS_PUBLISH = ev(
        'ENABLED_REDIS_PUBLISH',
        '0') == '1'
    REDIS_ADDRESS = ev(
        'REDIS_ADDRESS',
        'localhost:6379')
    REDIS_KEY = ev(
        'REDIS_KEY',
        'test_redis_key')
    REDIS_PASSWORD = ev(
        'REDIS_PASSWORD',
        None)
    REDIS_DB = int(ev(
        'REDIS_DB',
        '0'))
    REDIS_EXPIRE = ev(
        'REDIS_EXPIRE',
        None)

"""

import os
import sys
import json
import analysis_engine.options_dates as opt_dates


def ev(
        k,
        v):
    '''ev

    :param k: environment variable key
    :param v: environment variable value
    '''
    val = os.getenv(k, v)
    if val:
        return val.strip()
    return val
# end of ev


SUCCESS = 0
FAILED = 1
ERR = 2
EX = 3
NOT_RUN = 4
INVALID = 5
NOT_DONE = 6
NOT_SET = 7
EMPTY = 8
TRADE_OPEN = 9
TRADE_NOT_ENOUGH_FUNDS = 10
TRADE_FILLED = 11
TRADE_NO_SHARES_TO_SELL = 12
TRADE_EXPIRED = 13
TRADE_SHARES = 14
TRADE_VERTICAL_BULL_SPREAD = 15
TRADE_VERTICAL_BEAR_SPREAD = 16
TRADE_PROFITABLE = 17
TRADE_NOT_PROFITABLE = 18
TRADE_HIT_STOP_LOSS = 19
TRADE_HIT_STOP_LOSS_PERCENT = 20
TRADE_HIT_TAILING_STOP_LOSS = 21
TRADE_HIT_TAILING_STOP_LOSS_PERCENT = 22
TRADE_INVALID = 23
TRADE_ERROR = 24
TRADE_ENTRY = 25
TRADE_EXIT = 26
BACKTEST_FOUND_TRADE_PROFITABLE = 27
BACKTEST_FOUND_TRADE_NOT_PROFITABLE = 28
BACKTEST_FOUND_TRADE_NEVER_FILLED = 29  # limit order price never hit
BACKTEST_FOUND_TRADE_EXPIRED = 30  # trades assumed are expired after a day
SPREAD_VERTICAL_BULL = 31
SPREAD_VERTICAL_BEAR = 32
OPTION_CALL = 33
OPTION_PUT = 34
ALGO_PROFITABLE = 35
ALGO_NOT_PROFITABLE = 36
ALGO_ERROR = 37
ALGO_NOT_ACTIVE = 38
S3_FAILED = 39
REDIS_FAILED = 40
FILE_FAILED = 41
SLACK_FAILED = 42
ALGO_TIMESERIES_DAY = 43  # evaluate trade performance on daily-units
ALGO_TIMESERIES_MINUTE = 44  # evaluate trade performance on minute-units
ALGO_TRADE_INDICATOR_COUNTS = 45  # trade off num indicators said buy/sell
MISSING_TOKEN = 46

INDICATOR_CATEGORY_MOMENTUM = 60
INDICATOR_CATEGORY_OVERLAP = 61
INDICATOR_CATEGORY_PRICE = 62
INDICATOR_CATEGORY_VOLUME = 63
INDICATOR_CATEGORY_VOLATILITY = 64
INDICATOR_CATEGORY_SINGLE_CALL = 65
INDICATOR_CATEGORY_SINGLE_PUT = 66
INDICATOR_CATEGORY_BULL_CALL = 67
INDICATOR_CATEGORY_BEAR_PUT = 68
INDICATOR_CATEGORY_QUARTERLY = 69
INDICATOR_CATEGORY_YEARLY = 70
INDICATOR_CATEGORY_INCOME_STMT = 71
INDICATOR_CATEGORY_CASH_FLOW = 72
INDICATOR_CATEGORY_BALANCE_SHEET = 73
INDICATOR_CATEGORY_PRESS_RELEASE = 74
INDICATOR_CATEGORY_CUSTOM = 75
INDICATOR_CATEGORY_NEWS = 76
INDICATOR_CATEGORY_EARNINGS = 77
INDICATOR_CATEGORY_CSUITE = 78
INDICATOR_CATEGORY_SPLITS = 79
INDICATOR_CATEGORY_REVERSE_SPLITS = 80
INDICATOR_CATEGORY_DISTRIBUTIONS = 81
INDICATOR_CATEGORY_SPINOFFS = 82
INDICATOR_CATEGORY_MERGER_ACQ = 83
INDICATOR_CATEGORY_EXCHANGE_INCLUSION = 84
INDICATOR_CATEGORY_EXCHANGE_EXCLUSION = 85
INDICATOR_CATEGORY_TRIAL_POSITIVE = 86
INDICATOR_CATEGORY_TRIAL_NEGATIVE = 87
INDICATOR_CATEGORY_SHORT_SELLERS = 88
INDICATOR_CATEGORY_REAL_ESTATE = 89
INDICATOR_CATEGORY_HOUSING = 90
INDICATOR_CATEGORY_PIPELINE = 91
INDICATOR_CATEGORY_CONSTRUCTION = 94
INDICATOR_CATEGORY_FED = 93
INDICATOR_CATEGORY_UNKNOWN = 94

INDICATOR_TYPE_TECHNICAL = 200
INDICATOR_TYPE_FUNDAMENTAL = 201
INDICATOR_TYPE_NEWS = 202
INDICATOR_TYPE_SECTOR = 203
INDICATOR_TYPE_MARKET = 204
INDICATOR_TYPE_DIVIDEND = 205
INDICATOR_TYPE_CUSTOM = 206
INDICATOR_TYPE_UNKNOWN = 207

INDICATOR_USES_DAILY_DATA = 500
INDICATOR_USES_MINUTE_DATA = 501
INDICATOR_USES_QUOTE_DATA = 502
INDICATOR_USES_STATS_DATA = 503
INDICATOR_USES_PEERS_DATA = 504
INDICATOR_USES_NEWS_DATA = 505
INDICATOR_USES_FINANCIAL_DATA = 506
INDICATOR_USES_EARNINGS_DATA = 507
INDICATOR_USES_DIVIDENDS_DATA = 508
INDICATOR_USES_COMPANY_DATA = 509
INDICATOR_USES_PRICING_DATA = 510
INDICATOR_USES_OPTIONS_DATA = 511
INDICATOR_USES_CALLS_DATA = 512
INDICATOR_USES_PUTS_DATA = 513
INDICATOR_USES_DATA_UNSUPPORTED = 514
INDICATOR_USES_DATA_ANY = 515
INDICATOR_USES_TDCALLS_DATA = 516
INDICATOR_USES_TDPUTS_DATA = 517

INT_INDICATOR_NOT_PROCESSED = 600
INT_INDICATOR_IGNORE_ACTION = 601
INT_INDICATOR_BUY_ACTION = 602
INT_INDICATOR_SELL_ACTION = 603

INDICATOR_BUY = 'buy'
INDICATOR_SELL = 'sell'
INDICATOR_IGNORE = 'ignore'
INDICATOR_RESET = 'reset'

SA_MODE_PREPARE = 10000
SA_MODE_ANALYZE = 10001
SA_MODE_PREDICT = 10002
SA_MODE_EXTRACT = 10003
SA_MODE_SHOW_DATASET = 10004
SA_MODE_RESTORE_REDIS_DATASET = 10005
SA_MODE_RUN_ALGO = 10006
SA_MODE_SHOW_HISTORY_DATASET = 10007
SA_MODE_SHOW_REPORT_DATASET = 10008

SA_DATASET_TYPE_ALGO_READY = 20000
SA_DATASET_TYPE_TRADING_HISTORY = 20001
SA_DATASET_TYPE_TRADING_REPORT = 20002

PLOT_ACTION_SHOW = 21000
PLOT_ACTION_SAVE_TO_S3 = 21001
PLOT_ACTION_SAVE_AS_FILE = 21002

FETCH_MODE_ALL = 30000
FETCH_MODE_YHO = 30001
FETCH_MODE_IEX = 30002
FETCH_MODE_TD = 30003
FETCH_MODE_INTRADAY = 30004
FETCH_MODE_DAILY = 30005
FETCH_MODE_WEEKLY = 30006
FETCH_MODE_INITIAL = 30007

# GMT: Monday, January 19, 1970 12:26:40 PM
EPOCH_MINIMUM_DATE = 1600000

OPTIONS_UPPER_STRIKE = float(os.getenv(
    'OPTIONS_UPPER_STRIKE',
    '10.0'))
OPTIONS_LOWER_STRIKE = float(os.getenv(
    'OPTIONS_UPPER_STRIKE',
    '10.0'))
MAX_OPTIONS_UPPER_STRIKE = float(os.getenv(
    'MAX_OPTIONS_UPPER_STRIKE',
    '200'))
MAX_OPTIONS_LOWER_STRIKE = float(os.getenv(
    'MAX_OPTIONS_LOWER_STRIKE',
    '200'))
TRADIER_CONVERT_TO_DATETIME = [
    'date',
    'created',
    'ask_date',
    'bid_date',
    'trade_date'
]

# version of python
IS_PY2 = sys.version[0] == '2'
NUM_BYTES_IN_AN_MB = 1048576

APP_NAME = ev(
    'APP_NAME',
    'ae')
LOG_CONFIG_PATH = ev(
    'LOG_CONFIG_PATH',
    './analysis_engine/log/logging.json')
SSL_OPTIONS = {}
TRANSPORT_OPTIONS = {}
WORKER_BROKER_URL = ev(
    'WORKER_BROKER_URL',
    'redis://localhost:6379/13')
WORKER_BACKEND_URL = ev(
    'WORKER_BACKEND_URL',
    'redis://localhost:6379/14')
WORKER_CELERY_CONFIG_MODULE = ev(
    'WORKER_CELERY_CONFIG_MODULE',
    'analysis_engine.work_tasks.celery_config')
WORKER_TASKS = ev(
    'WORKER_TASKS',
    ('analysis_engine.work_tasks.task_run_algo,'
     'analysis_engine.work_tasks.get_new_pricing_data,'
     'analysis_engine.work_tasks.handle_pricing_update_task,'
     'analysis_engine.work_tasks.prepare_pricing_dataset,'
     'analysis_engine.work_tasks.publish_from_s3_to_redis,'
     'analysis_engine.work_tasks.publish_pricing_update,'
     'analysis_engine.work_tasks.task_screener_analysis,'
     'analysis_engine.work_tasks.publish_ticker_aggregate_from_s3'))
INCLUDE_TASKS = WORKER_TASKS.split(',')
CELERY_DISABLED = ev('CELERY_DISABLED', '0') == '1'

########################################
#
# Custom Variables
#
########################################
TICKER = ev(
    'TICKER',
    'SPY')
TICKER_ID = int(ev(
    'TICKER_ID',
    '1'))
DEFAULT_TICKERS = ev(
    'DEFAULT_TICKERS',
    'SPY,AMZN,TSLA,NFLX').split(',')
NEXT_EXP = opt_dates.option_expiration()
NEXT_EXP_STR = NEXT_EXP.strftime('%Y-%m-%d')
DAILY_S3_BUCKET_NAME = ev(
    'DAILY_S3_BUCKET_NAME',
    'daily')
MINUTE_S3_BUCKET_NAME = ev(
    'MINUTE_S3_BUCKET_NAME',
    'minute')
QUOTE_S3_BUCKET_NAME = ev(
    'QUOTE_S3_BUCKET_NAME',
    'quote')
STATS_S3_BUCKET_NAME = ev(
    'STATS_S3_BUCKET_NAME',
    'stats')
PEERS_S3_BUCKET_NAME = ev(
    'PEERS_S3_BUCKET_NAME',
    'peers')
NEWS_S3_BUCKET_NAME = ev(
    'NEWS_S3_BUCKET_NAME',
    'news')
FINANCIALS_S3_BUCKET_NAME = ev(
    'FINANCIALS_S3_BUCKET_NAME',
    'financials')
EARNINGS_S3_BUCKET_NAME = ev(
    'EARNINGS_S3_BUCKET_NAME',
    'earnings')
DIVIDENDS_S3_BUCKET_NAME = ev(
    'DIVIDENDS_S3_BUCKET_NAME',
    'dividends')
COMPANY_S3_BUCKET_NAME = ev(
    'COMPANY_S3_BUCKET_NAME',
    'company')
FETCH_MODE = ev(
    'FETCH_MODE',
    'all')
PREPARE_S3_BUCKET_NAME = ev(
    'PREPARE_S3_BUCKET_NAME',
    'prepared')
ANALYZE_S3_BUCKET_NAME = ev(
    'ANALYZE_S3_BUCKET_NAME',
    'analyzed')
SCREENER_S3_BUCKET_NAME = ev(
    'SCREENER_S3_BUCKET_NAME',
    'screener-data')
PRICING_S3_BUCKET_NAME = ev(
    'PRICING_S3_BUCKET_NAME',
    'pricing')
OPTIONS_S3_BUCKET_NAME = ev(
    'OPTIONS_S3_BUCKET_NAME',
    'options')
PREPARE_DATA_MIN_SIZE = 11
PLOT_COLORS = {
    'red': '#E74C3C',
    'feldspar': '#D19275',
    'copper': '#EDC393',
    'brown': '#6B4226',
    'orange': '#FF7D40',
    'maroon': '#800000',
    'gray': '#8B8989',
    'black': '#111111',
    'pink': '#FFCCCC',
    'green': '#2ECC71',
    'blue': '#3498db',
    'darkblue': '#000080',
    'lightgreen': '#C0FF3E',
    'darkgreen': '#385E0F',
    'gold': '#FFCC11',
    'yellow': '#FFE600',
    'volumetop': '#385E0F',
    'volume': '#ADFF2F',
    'high': '#CC1100',
    'low': '#164E71',
    'open': '#608DC0',
    'close': '#99CC32',
    'white': '#FFFFFF'
}

IEX_DAILY_DATE_FORMAT = '%Y-%b-%d'
IEX_MINUTE_DATE_FORMAT = '%Y-%m-%d %I:%M:%S %p'
IEX_TICK_DATE_FORMAT = '%Y-%m-%d %I:%M:%S %p'
IEX_QUOTE_DATE_FORMAT = '%B %d, %Y'
IEX_DATASETS_DEFAULT = [
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
IEX_INTRADAY_DATASETS = [
    'minute',
    'news'
]
IEX_DAILY_DATASETS = [
    'minute',
    'daily',
    'news'
]
IEX_WEEKLY_DATASETS = [
    'minute',
    'financials',
    'earnings',
    'dividends',
    'peers',
    'news',
    'company'
]
# Financial + Earnings are expensive
# so disabled for new users just
# getting started
IEX_INITIAL_DATASETS = [
    'daily',
    'minute',
    'stats',
    'news',
    'company'
]

BACKUP_DATASETS = [
    'tdcalls',
    'tdputs',
    'pricing',
    'options',
    'calls',
    'puts',
    'news1'
] + IEX_DATASETS_DEFAULT
if os.getenv('BACKUP_DATASETS', False):
    BACKUP_DATASETS = os.getenv('BACKUP_DATASETS', '').split(',')

COMMON_DATE_FORMAT = '%Y-%m-%d'
COMMON_TICK_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
CACHE_DICT_VERSION = 1

SLACK_WEBHOOK = ev(
    'SLACK_WEBHOOK',
    None)
SLACK_ACCESS_TOKEN = ev(
    'SLACK_ACCESS_TOKEN',
    None
)
SLACK_PUBLISH_PLOT_CHANNELS = ev(
    'SLACK_PUBLISH_PLOT_CHANNELS',
    None
)
PROD_SLACK_ALERTS = ev(
    'PROD_SLACK_ALERTS',
    '0')
DATASET_COLLECTION_VERSION = 1
DATASET_COLLECTION_SLACK_ALERTS = ev(
    'DATASET_COLLECTION_SLACK_ALERTS',
    '0')
SLACK_FINVIZ_ALL_COLUMNS = [
    'ticker',
    'price',
    'volume',
    'change',
    'pe',
    'market_cap',
    'company',
    'industry',
    'sector',
    'country'
]
SLACK_FINVIZ_COLUMNS = [
    'ticker',
    'price',
    'volume',
    'change',
    'pe',
    'market_cap'
]
ALGO_INPUT_COMPRESS = (ev(
    'ALGO_INPUT_COMPRESS',
    '0') == '1')
ALGO_LOAD_COMPRESS = (ev(
    'ALGO_LOAD_COMPRESS',
    '0') == '1')
ALGO_HISTORY_COMPRESS = (ev(
    'ALGO_HISTORY_COMPRESS',
    '1') == '1')
ALGO_HISTORY_VERSION = ev(
    'ALGO_HISTORY_VERSION',
    '1')
ALGO_REPORT_COMPRESS = (ev(
    'ALGO_REPORT_COMPRESS',
    '0') == '1')
ALGO_REPORT_VERSION = ev(
    'ALGO_REPORT_VERSION',
    '1')
DEFAULT_SERIALIZED_DATASETS = [
    'daily',
    'minute',
    'quote',
    'stats',
    'peers',
    'news1',
    'financials',
    'earnings',
    'dividends',
    'company',
    'news',
    'calls',
    'puts',
    'pricing',
    'tdcalls',
    'tdputs'
]
EMPTY_DF_STR = '[{}]'
EMPTY_DF_LIST = [{}]

########################################
#
# Algorithm Variables
#
########################################
ALGO_MODULE_PATH = ev(
    'ALGO_MODULE_PATH',
    '/opt/sa/analysis_engine/mocks/example_algo_minute.py')
ALGO_BASE_MODULE_PATH = ev(
    'ALGO_BASE_MODULE_PATH',
    '/opt/sa/analysis_engine/algo.py')
ALGO_MODULE_NAME = ev(
    'ALGO_MODULE_NAME',
    'example_algo_minute')
ALGO_VERSION = ev(
    'ALGO_VERSION',
    '1')
ALGO_BUYS_S3_BUCKET_NAME = ev(
    'ALGO_BUYS_S3_BUCKET_NAME',
    'algobuys')
ALGO_SELLS_S3_BUCKET_NAME = ev(
    'ALGO_SELLS_S3_BUCKET_NAME',
    'algosells')
ALGO_RESULT_S3_BUCKET_NAME = ev(
    'ALGO_RESULT_S3_BUCKET_NAME',
    'algoresult')
ALGO_EXTRACT_DATASET_S3_BUCKET_NAME = ev(
    'ALGO_EXTRACT_DATASET_S3_BUCKET_NAME',
    'algoready')
ALGO_READY_DATASET_S3_BUCKET_NAME = ev(
    'ALGO_READY_DATASET_S3_BUCKET_NAME',
    'algoready')
ALGO_HISTORY_DATASET_S3_BUCKET_NAME = ev(
    'ALGO_HISTORY_DATASET_S3_BUCKET_NAME',
    'algohistory')
ALGO_REPORT_DATASET_S3_BUCKET_NAME = ev(
    'ALGO_REPORT_DATASET_S3_BUCKET_NAME',
    'algoreport')
ALGO_BACKUP_DATASET_S3_BUCKET_NAME = ev(
    'ALGO_BACKUP_DATASET_S3_BUCKET_NAME',
    'algobackup')
ALGO_READY_DIR = ev(
    'ALGO_READY_DIR',
    '/tmp')
ALGO_EXTRACT_DIR = ev(
    'ALGO_EXTRACT_DIR',
    '/tmp')
ALGO_HISTORY_DIR = ev(
    'ALGO_HISTORY_HISTORY_DIR',
    '/tmp')
ALGO_REPORT_DIR = ev(
    'ALGO_REPORT_DIR',
    '/tmp')
ALGO_LOAD_DIR = ev(
    'ALGO_LOAD_DIR',
    '/tmp')
ALGO_BACKUP_DIR = ev(
    'ALGO_BACKUP_DIR',
    '/tmp')
ALGO_READY_REDIS_ADDRESS = ev(
    'ALGO_READY_REDIS_ADDRESS',
    'localhost:6379')
ALGO_EXTRACT_REDIS_ADDRESS = ev(
    'ALGO_EXTRACT_REDIS_ADDRESS',
    'localhost:6379')
ALGO_HISTORY_REDIS_ADDRESS = ev(
    'ALGO_HISTORY_REDIS_ADDRESS',
    'localhost:6379')
ALGO_REPORT_REDIS_ADDRESS = ev(
    'ALGO_REPORT_REDIS_ADDRESS',
    'localhost:6379')
ALGO_BACKUP_REDIS_ADDRESS = ev(
    'ALGO_BACKUP_REDIS_ADDRESS',
    'localhost:6379')

########################################
#
# Indicator Variables
#
########################################
INDICATOR_BASE_MODULE = ev(
    'INDICATOR_BASE_MODULE',
    'analysis_engine.indicators.base_indicator.BaseIndicator')
INDICATOR_BASE_MODULE_PATH = ev(
    'INDICATOR_BASE_MODULE_PATH',
    'analysis_engine/indicators/base_indicator.py')
INDICATOR_IGNORED_CONIGURABLE_KEYS = [
    'name',
    'module_path',
    'category',
    'type',
    'uses_data',
    'obj',
    'report'
]

########################################
#
# S3 Variables
#
########################################
ENABLED_S3_UPLOAD = ev(
    'ENABLED_S3_UPLOAD',
    '0') == '1'
S3_ACCESS_KEY = ev(
    'AWS_ACCESS_KEY_ID',
    'trexaccesskey')
S3_SECRET_KEY = ev(
    'AWS_SECRET_ACCESS_KEY',
    'trex123321')
S3_REGION_NAME = ev(
    'AWS_DEFAULT_REGION',
    'us-east-1')
S3_ADDRESS = ev(
    'S3_ADDRESS',
    '0.0.0.0:9000')
S3_SECURE = ev(
    'S3_SECURE',
    '0') == '1'
S3_BUCKET = ev(
    'S3_BUCKET',
    'pricing')
S3_COMPILED_BUCKET = ev(
    'S3_COMPILED_BUCKET',
    'compileddatasets')
S3_KEY = ev(
    'S3_KEY',
    'test_key')

########################################
#
# Redis Variables
#
########################################
ENABLED_REDIS_PUBLISH = ev(
    'ENABLED_REDIS_PUBLISH',
    '0') == '1'
REDIS_ADDRESS = ev(
    'REDIS_ADDRESS',
    'localhost:6379')
REDIS_KEY = ev(
    'REDIS_KEY',
    'test_redis_key')
REDIS_PASSWORD = ev(
    'REDIS_PASSWORD',
    None)
REDIS_DB = int(ev(
    'REDIS_DB',
    '0'))
REDIS_EXPIRE = ev(
    'REDIS_EXPIRE',
    None)

# copy these values over
# when calling child tasks from a
# parent where the engine is
# running inside a fully-dockerized
# environment like kubernetes
# or docker-compose
SERVICE_VALS = [
    'ticker',
    's3_address',
    's3_access_key',
    's3_secret_key',
    's3_bucket',
    's3_secure',
    's3_region_name',
    'redis_address',
    'redis_db',
    'redis_password',
    'redis_expire'
]


def get_status(
        status):
    """get_status

    Return the string label for an integer status code
    which should be one of the ones above.

    :param status: integer status code
    """
    if status == SUCCESS:
        return 'SUCCESS'
    elif status == FAILED:
        return 'FAILED'
    elif status == ERR:
        return 'ERR'
    elif status == EX:
        return 'EX'
    elif status == NOT_RUN:
        return 'NOT_RUN'
    elif status == INVALID:
        return 'INVALID'
    elif status == NOT_DONE:
        return 'NOT_DONE'
    elif status == NOT_SET:
        return 'NOT_SET'
    elif status == EMPTY:
        return 'EMPTY'
    elif status == SA_MODE_PREPARE:
        return 'SA_MODE_PREPARE'
    elif status == SA_MODE_ANALYZE:
        return 'SA_MODE_ANALYZE'
    elif status == SA_MODE_PREDICT:
        return 'SA_MODE_PREDICT'
    elif status == SA_MODE_EXTRACT:
        return 'SA_MODE_EXTRACT'
    elif status == SA_MODE_SHOW_DATASET:
        return 'SA_MODE_SHOW_DATASET'
    elif status == SA_MODE_RESTORE_REDIS_DATASET:
        return 'SA_MODE_RESTORE_REDIS_DATASET'
    elif status == SA_MODE_RUN_ALGO:
        return 'SA_MODE_RUN_ALGO'
    elif status == SA_MODE_SHOW_HISTORY_DATASET:
        return 'SA_MODE_SHOW_HISTORY_DATASET'
    elif status == SA_MODE_SHOW_REPORT_DATASET:
        return 'SA_MODE_SHOW_REPORT_DATASET'
    elif status == PLOT_ACTION_SHOW:
        return 'PLOT_ACTION_SHOW'
    elif status == PLOT_ACTION_SAVE_TO_S3:
        return 'PLOT_ACTION_SAVE_TO_S3'
    elif status == PLOT_ACTION_SAVE_AS_FILE:
        return 'PLOT_ACTION_SAVE_AS_FILE'
    elif status == TRADE_OPEN:
        return 'TRADE_OPEN'
    elif status == TRADE_NOT_ENOUGH_FUNDS:
        return 'TRADE_NOT_ENOUGH_FUNDS'
    elif status == TRADE_FILLED:
        return 'TRADE_FILLED'
    elif status == TRADE_NO_SHARES_TO_SELL:
        return 'TRADE_NO_SHARES_TO_SELL'
    elif status == TRADE_EXPIRED:
        return 'TRADE_EXPIRED'
    elif status == TRADE_SHARES:
        return 'TRADE_SHARES'
    elif status == TRADE_VERTICAL_BULL_SPREAD:
        return 'TRADE_VERTICAL_BULL_SPREAD'
    elif status == TRADE_VERTICAL_BEAR_SPREAD:
        return 'TRADE_VERTICAL_BEAR_SPREAD'
    elif status == TRADE_PROFITABLE:
        return 'TRADE_PROFITABLE'
    elif status == TRADE_NOT_PROFITABLE:
        return 'TRADE_NOT_PROFITABLE'
    elif status == TRADE_HIT_STOP_LOSS:
        return 'TRADE_HIT_STOP_LOSS'
    elif status == TRADE_HIT_STOP_LOSS_PERCENT:
        return 'TRADE_HIT_STOP_LOSS_PERCENT'
    elif status == TRADE_HIT_TAILING_STOP_LOSS:
        return 'TRADE_HIT_TAILING_STOP_LOSS'
    elif status == TRADE_HIT_TAILING_STOP_LOSS_PERCENT:
        return 'TRADE_HIT_TAILING_STOP_LOSS_PERCENT'
    elif status == TRADE_INVALID:
        return 'TRADE_INVALID'
    elif status == TRADE_ERROR:
        return 'TRADE_ERROR'
    elif status == TRADE_ENTRY:
        return 'TRADE_ENTRY'
    elif status == TRADE_EXIT:
        return 'TRADE_EXIT'
    elif status == BACKTEST_FOUND_TRADE_PROFITABLE:
        return 'BACKTEST_FOUND_TRADE_PROFITABLE'
    elif status == BACKTEST_FOUND_TRADE_NOT_PROFITABLE:
        return 'BACKTEST_FOUND_TRADE_NOT_PROFITABLE'
    elif status == BACKTEST_FOUND_TRADE_NEVER_FILLED:
        return 'BACKTEST_FOUND_TRADE_NEVER_FILLED'
    elif status == BACKTEST_FOUND_TRADE_EXPIRED:
        return 'BACKTEST_FOUND_TRADE_EXPIRED'
    elif status == SPREAD_VERTICAL_BULL:
        return 'SPREAD_VERTICAL_BULL'
    elif status == SPREAD_VERTICAL_BEAR:
        return 'SPREAD_VERTICAL_BEAR'
    elif status == OPTION_CALL:
        return 'OPTION_CALL'
    elif status == OPTION_PUT:
        return 'OPTION_PUT'
    elif status == ALGO_PROFITABLE:
        return 'ALGO_PROFITABLE'
    elif status == ALGO_NOT_PROFITABLE:
        return 'ALGO_NOT_PROFITABLE'
    elif status == ALGO_ERROR:
        return 'ALGO_ERROR'
    elif status == ALGO_NOT_ACTIVE:
        return 'ALGO_NOT_ACTIVE'
    elif status == S3_FAILED:
        return 'S3_FAILED'
    elif status == REDIS_FAILED:
        return 'REDIS_FAILED'
    elif status == FILE_FAILED:
        return 'FILE_FAILED'
    elif status == SLACK_FAILED:
        return 'SLACK_FAILED'
    elif status == ALGO_TIMESERIES_DAY:
        return 'ALGO_TIMESERIES_DAY'
    elif status == ALGO_TIMESERIES_MINUTE:
        return 'ALGO_TIMESERIES_MINUTE'
    elif status == ALGO_TRADE_INDICATOR_COUNTS:
        return 'ALGO_TRADE_INDICATOR_COUNTS'
    elif status == SA_DATASET_TYPE_ALGO_READY:
        return 'ALGO_READY'
    elif status == SA_DATASET_TYPE_TRADING_HISTORY:
        return 'TRADING_HISTORY'
    elif status == SA_DATASET_TYPE_TRADING_REPORT:
        return 'TRADING_REPORT'
    elif status == MISSING_TOKEN:
        return 'MISSING_TOKEN'
    else:
        return f'unsupported status={status}'
# end of get_status


def ppj(
        json_data):
    """ppj

    :param json_data: dictionary to convert to
                      a pretty-printed, multi-line string
    """
    return str(
        json.dumps(
            json_data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')))
# end of ppj


def to_float_str(
        val):
    """to_float_str

    convert the float to a string with 2 decimal points of
    precision

    :param val: float to change to a 2-decimal string
    """
    return str("%0.2f" % float(val))
# end of to_float_str


def to_f(
        val):
    """to_f

    truncate the float to 2 decimal points of
    precision

    :param val: float to change
    """
    if val is None:
        return None

    return float(to_float_str(val))
# end of to_f


def get_mb(
        num):
    """get_mb

    convert a the number of bytes (as an ``integer``)
    to megabytes with 2 decimal points of precision

    :param num: integer - number of bytes
    """
    return to_f(num / NUM_BYTES_IN_AN_MB)
# end get_mb


def get_percent_done(
        progress,
        total):
    """get_percent_done

    calculate percentage done to 2 decimal points of
    precision

    :param progress: progress counter
    :param total: total number of counts
    """
    return to_f(float(float(progress)/float(total)*100.00))
# end of get_percent_done


def is_celery_disabled(
        work_dict=None):
    """is_celery_disabled

    :param work_dict: request to check
    """
    env_disabled = ev('CELERY_DISABLED', '0') == '1'
    request_disabled = False
    if work_dict:
        request_disabled = work_dict.get('celery_disabled', False)
    return (env_disabled or request_disabled)
# end of is_celery_disabled


INDICATOR_TYPE_MAPPING = {
    'technical': INDICATOR_TYPE_TECHNICAL,
    'fundamental': INDICATOR_TYPE_FUNDAMENTAL,
    'news': INDICATOR_TYPE_NEWS,
    'sector': INDICATOR_TYPE_SECTOR,
    'market': INDICATOR_TYPE_MARKET,
    'dividend': INDICATOR_TYPE_DIVIDEND,
    'custom': INDICATOR_TYPE_CUSTOM,
    'unknown': INDICATOR_TYPE_UNKNOWN
}


INDICATOR_CATEGORY_MAPPING = {
    'momentum': INDICATOR_CATEGORY_MOMENTUM,
    'overlap': INDICATOR_CATEGORY_OVERLAP,
    'price': INDICATOR_CATEGORY_PRICE,
    'volume': INDICATOR_CATEGORY_VOLUME,
    'volatility': INDICATOR_CATEGORY_VOLATILITY,
    'single_call': INDICATOR_CATEGORY_SINGLE_CALL,
    'single_put': INDICATOR_CATEGORY_SINGLE_PUT,
    'bull_call': INDICATOR_CATEGORY_BULL_CALL,
    'bear_put': INDICATOR_CATEGORY_BEAR_PUT,
    'quarterly': INDICATOR_CATEGORY_QUARTERLY,
    'yearly': INDICATOR_CATEGORY_YEARLY,
    'income_statement': INDICATOR_CATEGORY_INCOME_STMT,
    'cash_flow': INDICATOR_CATEGORY_CASH_FLOW,
    'balance_sheet': INDICATOR_CATEGORY_BALANCE_SHEET,
    'press_release': INDICATOR_CATEGORY_PRESS_RELEASE,
    'custom': INDICATOR_CATEGORY_CUSTOM,
    'news': INDICATOR_CATEGORY_NEWS,
    'earnings': INDICATOR_CATEGORY_EARNINGS,
    'csuite': INDICATOR_CATEGORY_CSUITE,
    'splits': INDICATOR_CATEGORY_SPLITS,
    'rev_splits': INDICATOR_CATEGORY_REVERSE_SPLITS,
    'distributions': INDICATOR_CATEGORY_DISTRIBUTIONS,
    'spinoffs': INDICATOR_CATEGORY_SPINOFFS,
    'merger_acq': INDICATOR_CATEGORY_MERGER_ACQ,
    'exchange_inclusion': INDICATOR_CATEGORY_EXCHANGE_INCLUSION,
    'exchange_exclusion': INDICATOR_CATEGORY_EXCHANGE_EXCLUSION,
    'trial_positive': INDICATOR_CATEGORY_TRIAL_POSITIVE,
    'trial_negative': INDICATOR_CATEGORY_TRIAL_NEGATIVE,
    'short_sellers': INDICATOR_CATEGORY_SHORT_SELLERS,
    'real_estate': INDICATOR_CATEGORY_REAL_ESTATE,
    'housing': INDICATOR_CATEGORY_HOUSING,
    'pipeline': INDICATOR_CATEGORY_PIPELINE,
    'construction': INDICATOR_CATEGORY_CONSTRUCTION,
    'fed': INDICATOR_CATEGORY_FED,
    'unknown': INDICATOR_CATEGORY_UNKNOWN,
}

INDICATOR_USES_DATA_MAPPING = {
    'daily': INDICATOR_USES_DAILY_DATA,
    'minute': INDICATOR_USES_MINUTE_DATA,
    'quote': INDICATOR_USES_QUOTE_DATA,
    'stats': INDICATOR_USES_STATS_DATA,
    'peers': INDICATOR_USES_PEERS_DATA,
    'news': INDICATOR_USES_NEWS_DATA,
    'financials': INDICATOR_USES_FINANCIAL_DATA,
    'earnings': INDICATOR_USES_EARNINGS_DATA,
    'dividends': INDICATOR_USES_DIVIDENDS_DATA,
    'company': INDICATOR_USES_COMPANY_DATA,
    'pricing': INDICATOR_USES_PRICING_DATA,
    'options': INDICATOR_USES_OPTIONS_DATA,
    'calls': INDICATOR_USES_CALLS_DATA,
    'puts': INDICATOR_USES_PUTS_DATA,
    'unsupported': INDICATOR_USES_DATA_UNSUPPORTED,
    'tdcalls': INDICATOR_USES_TDCALLS_DATA,
    'tdputs': INDICATOR_USES_TDPUTS_DATA,
    'any': INDICATOR_USES_DATA_ANY
}


INDICATOR_ACTIONS = {
    INDICATOR_RESET: INT_INDICATOR_NOT_PROCESSED,
    INDICATOR_IGNORE: INT_INDICATOR_IGNORE_ACTION,
    INDICATOR_BUY: INT_INDICATOR_BUY_ACTION,
    INDICATOR_SELL: INT_INDICATOR_SELL_ACTION
}


ALGO_TIMESERIES = {
    'daily': ALGO_TIMESERIES_DAY,
    'minute': ALGO_TIMESERIES_MINUTE,
    'intraday': ALGO_TIMESERIES_MINUTE
}


def get_indicator_type_as_int(
        val=None):
    """get_indicator_type_as_int

    convert the string to the ``INDICATOR_TYPE_MAPPING``
    integer value

    :param val: integer to lookup in the ``INDICATOR_TYPE_MAPPING``
        dictionary
    """
    if not val:
        return INDICATOR_TYPE_UNKNOWN
    else:
        if val in INDICATOR_TYPE_MAPPING:
            return INDICATOR_TYPE_MAPPING[val]
        else:
            return INDICATOR_TYPE_UNKNOWN
    # if supported or not
# end of get_indicator_type_as_int


def get_indicator_category_as_int(
        val=None):
    """get_indicator_category_as_int

    convert the string to the ``INDICATOR_CATEGORY_MAPPING``
    integer value

    :param val: integer to lookup in the ``INDICATOR_CATEGORY_MAPPING``
        dictionary
    """
    if not val:
        return INDICATOR_CATEGORY_UNKNOWN
    else:
        if val in INDICATOR_CATEGORY_MAPPING:
            return INDICATOR_CATEGORY_MAPPING[val]
        else:
            return INDICATOR_CATEGORY_UNKNOWN
    # if supported or not
# end of get_indicator_category_as_int


def get_indicator_uses_data_as_int(
        val=None):
    """get_indicator_uses_data_as_int

    convert the string to the ``INDICATOR_USES_DATA_MAPPING``
    integer value

    :param val: integer to lookup in the ``INDICATOR_USES_DATA_MAPPING``
        dictionary
    """
    if not val:
        return INDICATOR_USES_DATA_ANY
    else:
        if val in INDICATOR_USES_DATA_MAPPING:
            return INDICATOR_USES_DATA_MAPPING[val]
        else:
            return INDICATOR_USES_DATA_UNSUPPORTED
    # if supported or not
# end of get_indicator_uses_data_as_int


def get_algo_timeseries_from_int(
        val):
    """get_algo_timeseries_from_int

    convert the integer value to the timeseries string
    found in the ``analysis_engine.consts.ALGO_TIMESERIES``
    dictionary

    :param val: integer value for finding the
        string timeseries label
    """
    for a in ALGO_TIMESERIES:
        if ALGO_TIMESERIES[a] == val:
            return a
    return f'unsupported algorithm timeseries value={val}'
# end of get_algo_timeseries_from_int


def is_df(
        df):
    """is_df

    Test if ``df`` is a valid ``pandas.DataFrame``

    :param df: ``pandas.DataFrame``
    """
    return (
        hasattr(df, 'to_json'))
# end of is_df


def get_redis_host_and_port(
        addr=None,
        req=None):
    """get_redis_host_and_port

    parse the env ``REDIS_ADDRESS`` or ``addr`` string
    or a dictionary ``req`` and
    return a tuple for (host (str), port (int))

    :param addr: optional - string redis address to parse
        format is ``host:port``
    :param req: optional - dictionary where the host and port
        are under the keys ``redis_host`` and ``redis_port``
    """
    use_addr = REDIS_ADDRESS
    redis_host = None
    redis_port = None
    if addr:
        use_addr = addr
    split_arr = use_addr.split(':')
    redis_host = split_arr[0]
    redis_port = int(split_arr[1])
    if req:
        redis_host = req.get(
            'redis_host',
            redis_host)
        redis_port = int(req.get(
            'redis_port',
            redis_port))
    return redis_host, redis_port
# end of get_redis_host_and_port
