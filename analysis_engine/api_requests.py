"""
Helpers and examples for supported API Requests that each Celery
Task supports:

- analysis_engine.work_tasks.get_new_pricing_data
- analysis_engine.work_tasks.handle_pricing_update_task
- analysis_engine.work_tasks.publish_pricing_update

"""

import datetime
import analysis_engine.iex.utils as iex_utils
import pandas as pd
from functools import lru_cache
from analysis_engine.consts import to_f
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import COMMON_DATE_FORMAT
from analysis_engine.consts import COMMON_TICK_DATE_FORMAT
from analysis_engine.consts import CACHE_DICT_VERSION
from analysis_engine.consts import DAILY_S3_BUCKET_NAME
from analysis_engine.consts import MINUTE_S3_BUCKET_NAME
from analysis_engine.consts import QUOTE_S3_BUCKET_NAME
from analysis_engine.consts import STATS_S3_BUCKET_NAME
from analysis_engine.consts import PEERS_S3_BUCKET_NAME
from analysis_engine.consts import NEWS_S3_BUCKET_NAME
from analysis_engine.consts import FINANCIALS_S3_BUCKET_NAME
from analysis_engine.consts import EARNINGS_S3_BUCKET_NAME
from analysis_engine.consts import DIVIDENDS_S3_BUCKET_NAME
from analysis_engine.consts import COMPANY_S3_BUCKET_NAME
from analysis_engine.consts import PREPARE_S3_BUCKET_NAME
from analysis_engine.consts import ANALYZE_S3_BUCKET_NAME
from analysis_engine.consts import SCREENER_S3_BUCKET_NAME
from analysis_engine.consts import ALGO_BUYS_S3_BUCKET_NAME
from analysis_engine.consts import ALGO_SELLS_S3_BUCKET_NAME
from analysis_engine.consts import ALGO_RESULT_S3_BUCKET_NAME
from analysis_engine.consts import S3_BUCKET
from analysis_engine.consts import S3_COMPILED_BUCKET
from analysis_engine.consts import SERVICE_VALS
from analysis_engine.consts import IEX_DATASETS_DEFAULT
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import TRADE_OPEN
from analysis_engine.consts import TRADE_NOT_ENOUGH_FUNDS
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import TRADE_NO_SHARES_TO_SELL
from analysis_engine.consts import TRADE_ENTRY
from analysis_engine.consts import TRADE_EXIT
from analysis_engine.consts import TRADE_PROFITABLE
from analysis_engine.consts import TRADE_NOT_PROFITABLE
from analysis_engine.consts import TRADE_ERROR
from analysis_engine.consts import SPREAD_VERTICAL_BULL
from analysis_engine.consts import SPREAD_VERTICAL_BEAR
from analysis_engine.consts import OPTION_CALL
from analysis_engine.consts import OPTION_PUT
from analysis_engine.consts import ALGO_PROFITABLE
from analysis_engine.consts import ALGO_NOT_PROFITABLE
from analysis_engine.consts import ALGO_ERROR
from analysis_engine.utils import get_last_close_str
from analysis_engine.utils import utc_date_str
from analysis_engine.utils import utc_now_str
from analysis_engine.utils import get_date_from_str
from analysis_engine.iex.consts import FETCH_DAILY
from analysis_engine.iex.consts import FETCH_MINUTE
from analysis_engine.iex.consts import FETCH_QUOTE
from analysis_engine.iex.consts import FETCH_STATS
from analysis_engine.iex.consts import FETCH_PEERS
from analysis_engine.iex.consts import FETCH_NEWS
from analysis_engine.iex.consts import FETCH_FINANCIALS
from analysis_engine.iex.consts import FETCH_EARNINGS
from analysis_engine.iex.consts import FETCH_DIVIDENDS
from analysis_engine.iex.consts import FETCH_COMPANY
from analysis_engine.iex.consts import DATAFEED_DAILY
from analysis_engine.iex.consts import DATAFEED_MINUTE
from analysis_engine.iex.consts import DATAFEED_QUOTE
from analysis_engine.iex.consts import DATAFEED_STATS
from analysis_engine.iex.consts import DATAFEED_PEERS
from analysis_engine.iex.consts import DATAFEED_NEWS
from analysis_engine.iex.consts import DATAFEED_FINANCIALS
from analysis_engine.iex.consts import DATAFEED_EARNINGS
from analysis_engine.iex.consts import DATAFEED_DIVIDENDS
from analysis_engine.iex.consts import DATAFEED_COMPANY


def get_ds_dict(
        ticker,
        base_key=None,
        ds_id=None,
        label=None,
        service_dict=None):
    """get_ds_dict

    Get a dictionary with all cache keys for a ticker and return
    the dictionary. Use this method to decouple your apps
    from the underlying cache key implementations (if you
    do not need them).

    :param ticker: ticker
    :param base_key: optional - base key that is prepended
                     in all cache keys
    :param ds_id: optional - dataset id (useful for
                  external database id)
    :param label: optional - tracking label in the logs
    :param service_dict: optional - parent call functions and Celery
                         tasks can use this dictionary to seed the
                         common service routes and endpoints. Refer
                         to ``analysis_engine.consts.SERVICE_VALS``
                         for automatically-copied over keys by this
                         helper.
    """

    if not ticker:
        raise Exception('please pass in a ticker')

    use_base_key = base_key
    if not use_base_key:
        use_base_key = '{}_{}'.format(
            ticker,
            get_last_close_str(fmt=COMMON_DATE_FORMAT))

    date_str = utc_date_str(fmt=COMMON_DATE_FORMAT)
    now_str = utc_now_str(fmt=COMMON_TICK_DATE_FORMAT)

    daily_redis_key = '{}_daily'.format(use_base_key)
    minute_redis_key = '{}_minute'.format(use_base_key)
    quote_redis_key = '{}_quote'.format(use_base_key)
    stats_redis_key = '{}_stats'.format(use_base_key)
    peers_redis_key = '{}_peers'.format(use_base_key)
    news_iex_redis_key = '{}_news1'.format(use_base_key)
    financials_redis_key = '{}_financials'.format(use_base_key)
    earnings_redis_key = '{}_earnings'.format(use_base_key)
    dividends_redis_key = '{}_dividends'.format(use_base_key)
    company_redis_key = '{}_company'.format(use_base_key)
    options_yahoo_redis_key = '{}_options'.format(use_base_key)
    pricing_yahoo_redis_key = '{}_pricing'.format(use_base_key)
    news_yahoo_redis_key = '{}_news'.format(use_base_key)

    ds_cache_dict = {
        'daily': daily_redis_key,
        'minute': minute_redis_key,
        'quote': quote_redis_key,
        'stats': stats_redis_key,
        'peers': peers_redis_key,
        'news1': news_iex_redis_key,
        'financials': financials_redis_key,
        'earnings': earnings_redis_key,
        'dividends': dividends_redis_key,
        'company': company_redis_key,
        'options': options_yahoo_redis_key,
        'pricing': pricing_yahoo_redis_key,
        'news': news_yahoo_redis_key,
        'ticker': ticker,
        'ds_id': ds_id,
        'label': label,
        'created': now_str,
        'date': date_str,
        'manifest_key': use_base_key,
        'version': CACHE_DICT_VERSION
    }

    # set keys/values for redis/minio from the
    # service_dict - helper method for
    # launching job chains
    if service_dict:
        for k in SERVICE_VALS:
            ds_cache_dict[k] = service_dict[k]

    return ds_cache_dict
# end of get_ds_dict


def build_get_new_pricing_request(
        label=None):
    """build_get_new_pricing_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.get_new_pricing_data

    Used for testing: run_get_new_pricing_data(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    base_key = '{}_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = S3_BUCKET
    s3_key = base_key
    redis_key = base_key
    use_strike = None
    contract_type = 'C'
    get_pricing = True
    get_news = True
    get_options = True

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        'strike': use_strike,
        'contract': contract_type,
        'get_pricing': get_pricing,
        'get_news': get_news,
        'get_options': get_options
    }

    if label:
        work['label'] = label

    return work
# end of build_get_new_pricing_request


@lru_cache(1)
def build_cache_ready_pricing_dataset(
        label=None):
    """build_cache_ready_pricing_dataset

    Build a cache-ready pricing dataset to replicate
    the ``get_new_pricing_data`` task

    :param label: log label to use
    """

    pricing_dict = {
        'ask': 0.0,
        'askSize': 8,
        'averageDailyVolume10Day': 67116380,
        'averageDailyVolume3Month': 64572187,
        'bid': 0.0,
        'bidSize': 10,
        'close': 287.6,
        'currency': 'USD',
        'esgPopulated': False,
        'exchange': 'PCX',
        'exchangeDataDelayedBy': 0,
        'exchangeTimezoneName': 'America/New_York',
        'exchangeTimezoneShortName': 'EDT',
        'fiftyDayAverage': 285.21735,
        'fiftyDayAverageChange': 2.8726501,
        'fiftyDayAverageChangePercent': 0.010071794,
        'fiftyTwoWeekHigh': 291.74,
        'fiftyTwoWeekHighChange': -3.649994,
        'fiftyTwoWeekHighChangePercent': -0.012511119,
        'fiftyTwoWeekLow': 248.02,
        'fiftyTwoWeekLowChange': 40.069992,
        'fiftyTwoWeekLowChangePercent': 0.16155952,
        'fiftyTwoWeekRange': '248.02 - 291.74',
        'financialCurrency': 'USD',
        'fullExchangeName': 'NYSEArca',
        'gmtOffSetMilliseconds': -14400000,
        'high': 289.03,
        'language': 'en-US',
        'longName': 'SPDR S&amp;P 500 ETF',
        'low': 287.88,
        'market': 'us_market',
        'marketCap': 272023797760,
        'marketState': 'POSTPOST',
        'messageBoardId': 'finmb_6160262',
        'open': 288.74,
        'postMarketChange': 0.19998169,
        'postMarketChangePercent': 0.06941398,
        'postMarketPrice': 288.3,
        'postMarketTime': 1536623987,
        'priceHint': 2,
        'quoteSourceName': 'Delayed Quote',
        'quoteType': 'ETF',
        'region': 'US',
        'regularMarketChange': 0.48999023,
        'regularMarketChangePercent': 0.17037213,
        'regularMarketDayHigh': 289.03,
        'regularMarketDayLow': 287.88,
        'regularMarketDayRange': '287.88 - 289.03',
        'regularMarketOpen': 288.74,
        'regularMarketPreviousClose': 287.6,
        'regularMarketPrice': 288.09,
        'regularMarketTime': 1536609602,
        'regularMarketVolume': 50210903,
        'sharesOutstanding': 944232000,
        'shortName': 'SPDR S&P 500',
        'sourceInterval': 15,
        'symbol': 'SPY',
        'tradeable': True,
        'trailingThreeMonthNavReturns': 7.71,
        'trailingThreeMonthReturns': 7.63,
        'twoHundredDayAverage': 274.66153,
        'twoHundredDayAverageChange': 13.428467,
        'twoHundredDayAverageChangePercent': 0.048890963,
        'volume': 50210903,
        'ytdReturn': 9.84
    }
    calls_df_as_json = pd.DataFrame([{
        'ask': 106,
        'bid': 105.36,
        'change': 4.0899963,
        'contractSize': 'REGULAR',
        'contractSymbol': 'SPY181019P00380000',
        'currency': 'USD',
        'expiration': 1539907200,
        'impliedVolatility': 1.5991230981,
        'inTheMoney': True,
        'lastPrice': 91.82,
        'lastTradeDate': 1539027901,
        'openInterest': 0,
        'percentChange': 4.4543633,
        'strike': 380,
        'volume': 37
    }]).to_json(
        orient='records')
    puts_df_as_json = pd.DataFrame([{
        'ask': 106,
        'bid': 105.36,
        'change': 4.0899963,
        'contractSize': 'REGULAR',
        'contractSymbol': 'SPY181019P00380000',
        'currency': 'USD',
        'expiration': 1539907200,
        'impliedVolatility': 1.5991230981,
        'inTheMoney': True,
        'lastPrice': 91.82,
        'lastTradeDate': 1539027901,
        'openInterest': 0,
        'percentChange': 4.4543633,
        'strike': 380,
        'volume': 37
    }]).to_json(
        orient='records')
    news_list = [
        {
            'd': '16 hours ago',
            's': 'Yahoo Finance',
            'sp': 'Some Title 1',
            'sru': 'http://news.google.com/news/url?values',
            't': 'Some Title 1',
            'tt': '1493311950',
            'u': 'http://finance.yahoo.com/news/url1',
            'usg': 'ke1'
        },
        {
            'd': '18 hours ago',
            's': 'Yahoo Finance',
            'sp': 'Some Title 2',
            'sru': 'http://news.google.com/news/url?values',
            't': 'Some Title 2',
            'tt': '1493311950',
            'u': 'http://finance.yahoo.com/news/url2',
            'usg': 'key2'
        }
    ]

    options_dict = {
        'exp_date': '2018-10-19',
        'calls': calls_df_as_json,
        'puts': puts_df_as_json,
        'num_calls': 1,
        'num_puts': 1
    }

    cache_data = {
        'news': news_list,
        'options': options_dict,
        'pricing': pricing_dict
    }
    return cache_data
# end of build_cache_ready_pricing_dataset


def build_publish_pricing_request(
        label=None):
    """build_publish_pricing_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.publisher_pricing_update

    Used for testing: run_publish_pricing_update(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    base_key = '{}_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = S3_BUCKET
    s3_key = base_key
    redis_key = base_key
    use_strike = None
    contract_type = 'C'
    use_data = build_cache_ready_pricing_dataset()

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        'strike': use_strike,
        'contract': contract_type,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        'data': use_data
    }

    if label:
        work['label'] = label

    return work
# end of build_publish_pricing_request


def build_publish_from_s3_to_redis_request(
        label=None):
    """build_publish_from_s3_to_redis_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.publish_from_s3_to_redis

    Used for testing: run_publish_from_s3_to_redis(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    base_key = '{}_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = S3_BUCKET
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_publish_from_s3_to_redis_request


def build_publish_ticker_aggregate_from_s3_request(
        label=None):
    """build_publish_ticker_aggregate_from_s3_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.publish_ticker_aggregate_from_s3

    Used for testing: run_publish_ticker_aggregate_from_s3(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    s3_bucket_name = S3_BUCKET
    s3_compiled_bucket_name = S3_COMPILED_BUCKET
    s3_key = '{}_latest'.format(ticker)
    redis_key = '{}_latest'.format(ticker)
    s3_enabled = True
    redis_enabled = True

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_compiled_bucket': s3_compiled_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_publish_ticker_aggregate_from_s3_request


def build_prepare_dataset_request(
        label=None):
    """build_prepare_dataset_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.prepare_pricing_dataset

    Used for testing: run_prepare_pricing_dataset(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    base_key = '{}_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = S3_BUCKET
    s3_key = base_key
    redis_key = base_key
    s3_prepared_bucket_name = PREPARE_S3_BUCKET_NAME
    s3_prepared_key = '{}.csv'.format(
        base_key)
    redis_prepared_key = '{}'.format(
        base_key)
    ignore_columns = None
    s3_enabled = True
    redis_enabled = True

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        'prepared_s3_key': s3_prepared_key,
        'prepared_s3_bucket': s3_prepared_bucket_name,
        'prepared_redis_key': redis_prepared_key,
        'ignore_columns': ignore_columns,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_prepare_dataset_request


def build_analyze_dataset_request(
        label=None):
    """build_analyze_dataset_request

    Build a sample Celery task API request:
    analysis_engine.work_tasks.analyze_pricing_dataset

    Used for testing: run_analyze_pricing_dataset(work)

    :param label: log label to use
    """
    ticker = TICKER
    ticker_id = TICKER_ID
    base_key = '{}_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = PREPARE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_analyzed_bucket_name = ANALYZE_S3_BUCKET_NAME
    s3_analyzed_key = '{}.csv'.format(
        base_key)
    redis_analyzed_key = '{}'.format(
        base_key)
    ignore_columns = None
    s3_enabled = True
    redis_enabled = True

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        'analyzed_s3_key': s3_analyzed_key,
        'analyzed_s3_bucket': s3_analyzed_bucket_name,
        'analyzed_redis_key': redis_analyzed_key,
        'ignore_columns': ignore_columns,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_analyze_dataset_request


"""
IEX API Requests
"""


def build_iex_fetch_daily_request(
        label=None):
    """build_iex_fetch_daily_request

    Fetch daily data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_daily_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = DAILY_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_DAILY,
        'fd_type': DATAFEED_DAILY,
        'ticker': ticker,
        'timeframe': '5y',
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_daily_request


def build_iex_fetch_minute_request(
        label=None):
    """build_iex_fetch_minute_request

    Fetch `minute data <https://iextrading.com/developer/docs/#chart>`__
    from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_minute_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = MINUTE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_MINUTE,
        'fd_type': DATAFEED_MINUTE,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        'last_close': None,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_minute_request


def build_iex_fetch_quote_request(
        label=None):
    """build_iex_fetch_quote_request

    Fetch `quote data <https://iextrading.com/developer/docs/#quote>`__
    from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_quote_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = QUOTE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_QUOTE,
        'fd_type': DATAFEED_QUOTE,
        'ticker': ticker,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_quote_request


def build_iex_fetch_stats_request(
        label=None):
    """build_iex_fetch_stats_request

    Fetch statistic data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_stat_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = STATS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_STATS,
        'fd_type': DATAFEED_STATS,
        'ticker': ticker,
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_stats_request


def build_iex_fetch_peers_request(
        label=None):
    """build_iex_fetch_peers_request

    Fetch peer data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_peer_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = PEERS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_PEERS,
        'fd_type': DATAFEED_PEERS,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_peers_request


def build_iex_fetch_news_request(
        label=None):
    """build_iex_fetch_news_request

    Fetch news data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_news_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = NEWS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_NEWS,
        'fd_type': DATAFEED_NEWS,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_news_request


def build_iex_fetch_financials_request(
        label=None):
    """build_iex_fetch_financials_request

    Fetch financial data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_financial_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = FINANCIALS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_FINANCIALS,
        'fd_type': DATAFEED_FINANCIALS,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_financials_request


def build_iex_fetch_earnings_request(
        label=None):
    """build_iex_fetch_earnings_request

    Fetch earnings data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_earning_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = EARNINGS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_EARNINGS,
        'fd_type': DATAFEED_EARNINGS,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_earnings_request


def build_iex_fetch_dividends_request(
        label=None):
    """build_iex_fetch_dividends_request

    Fetch dividend data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_dividend_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = DIVIDENDS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_DIVIDENDS,
        'fd_type': DATAFEED_DIVIDENDS,
        'ticker': ticker,
        'timeframe': '2y',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_dividends_request


def build_iex_fetch_company_request(
        label=None):
    """build_iex_fetch_company_request

    Fetch company data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_company_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = COMPANY_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_COMPANY,
        'fd_type': DATAFEED_COMPANY,
        'ticker': ticker,
        'timeframe': '1d',
        'from': iex_utils.last_month().strftime(
            '%Y-%m-%d %H:%M:%S'),
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_iex_fetch_company_request


def build_screener_analysis_request(
        ticker=None,
        tickers=None,
        fv_urls=None,
        fetch_mode='iex',
        iex_datasets=IEX_DATASETS_DEFAULT,
        determine_sells=None,
        determine_buys=None,
        label='screener'):
    """build_screener_analysis_request

    Build a dictionary request for the task:
    ``analysis_engine.work_tasks.run_screener_analysis``

    :param ticker: ticker to add to the analysis
    :param tickers: tickers to add to the analysis
    :param fv_urls: finviz urls
    :param fetch_mode: supports pulling from ``iex``,
        ``yahoo``, ``all`` (defaults to ``iex``)
    :param iex_datasets: datasets to fetch from
        ``iex`` (defaults to ``analysis_engine.con
        sts.IEX_DATASETS_DEFAULT``)
    :param determine_sells: string custom Celery task
        name for handling sell-side processing
    :param determine_buys: string custom Celery task
        name for handling buy-side processing
    :param label: log tracking label
    :return: initial request dictionary:
        ::

            req = {
                'tickers': use_tickers,
                'fv_urls': use_urls,
                'fetch_mode': fetch_mode,
                'iex_datasets': iex_datasets,
                's3_bucket': s3_bucket_name,
                's3_enabled': s3_enabled,
                'redis_enabled': redis_enabled,
                'determine_sells': determine_sells,
                'determine_buys': determine_buys,
                'label': label
            }
    """
    use_urls = []
    if fv_urls:
        for f in fv_urls:
            if f not in use_urls:
                use_urls.append(f)

    use_tickers = tickers
    if ticker:
        if not tickers:
            use_tickers = [
                ticker
            ]
        if ticker.upper() not in use_tickers:
            use_tickers.append(ticker.upper())

    s3_bucket_name = SCREENER_S3_BUCKET_NAME
    s3_enabled = True
    redis_enabled = True

    req = {
        'tickers': use_tickers,
        'urls': use_urls,
        'fetch_mode': fetch_mode,
        'iex_datasets': iex_datasets,
        's3_bucket': s3_bucket_name,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'determine_sells': determine_sells,
        'determine_buys': determine_buys,
        'label': label
    }
    return req
# end build_screener_analysis_request


def build_algo_request(
        ticker=None,
        tickers=None,
        use_key=None,
        start_date=None,
        end_date=None,
        datasets=None,
        balance=None,
        num_shares=None,
        cache_freq='daily',
        label='algo'):
    """build_algo_request

    :param ticker: ticker
    :param tickers: optional - list of tickers
    :param use_key: redis and s3 to store the algo result
    :param start_date: string date format ``YYYY-MM-DD HH:MM:SS``
    :param end_date: string date format ``YYYY-MM-DD HH:MM:SS``
    :param datasets: list of string dataset types
    :param balance: starting capital balance
    :param num_shares: integer number of starting shares
    :param num_shares: optional - cache frequency (``daily`` is default)
    :param label: optional - algo log tracking name
    """
    use_tickers = []
    if ticker:
        use_tickers = [
            ticker.upper()
        ]
    if tickers:
        for t in tickers:
            if t not in use_tickers:
                use_tickers.append(t.upper())

    s3_bucket_name = ALGO_RESULT_S3_BUCKET_NAME
    s3_key = use_key
    redis_key = use_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'tickers': use_tickers,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'extract_datasets': [],
        'cache_freq': cache_freq,
        'version': 1,
        'label': label
    }

    start_date_val = get_date_from_str(start_date)
    end_date_val = get_date_from_str(end_date)
    if start_date_val >= end_date_val:
        raise Exception(
            'Invalid start_date={} must be less than end_date={}'.format(
                start_date,
                end_date))

    use_dates = []
    new_dataset = None
    cur_date = start_date_val
    while cur_date <= end_date_val:
        if cur_date.weekday() < 5:
            for t in use_tickers:
                if cache_freq == 'daily':
                    new_dataset = '{}_{}'.format(
                        t,
                        cur_date.strftime(
                            COMMON_DATE_FORMAT))
                else:
                    new_dataset = '{}_{}'.format(
                        t,
                        cur_date.strftime(
                            COMMON_TICK_DATE_FORMAT))
                if new_dataset:
                    use_dates.append(new_dataset)
                new_dataset = None
            # end for all tickers
        # end of valid days M-F
        if cache_freq == 'daily':
            cur_date += datetime.timedelta(days=1)
        else:
            cur_date += datetime.timedelta(minute=1)
    # end of walking all dates to add

    work['extract_datasets'] = use_dates

    return work
# end of build_algo_request


def build_option_spread_details(
        trade_type,
        spread_type,
        option_type,
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_option_spread_details

    Calculate pricing information for supported spreads
    including max loss, max profit, and mid price (break
    even coming soon)

    :param trade_type: entry (``TRADE_ENTRY``) or
        exit (``TRADE_EXIT``) of a spread position
    :param spread_type: vertical bull (``SPREAD_VERTICAL_BULL``)
        and vertical bear (``SPREAD_VERTICAL_BEAR``)
        are the only supported calculations for now
    :param option_type: call (``OPTION_CALL``) or put
        (``OPTION_PUT``)
    :param close: closing price of the underlying
        asset
    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    details = {
        'status': NOT_RUN,
        'trade_type': trade_type,
        'spread_type': spread_type,
        'option_type': option_type,
        'num_contracts': num_contracts,
        'low_strike': low_strike,
        'low_bid': low_bid,
        'low_ask': low_ask,
        'high_strike': high_strike,
        'high_bid': high_bid,
        'high_ask': high_ask,
        'cost': None,
        'revenue': None,
        'low_bidask_mid': None,
        'high_bidask_mid': None,
        'mid_price': None,
        'nat_price': None,
        'strike_width': None,
        'break_even': None,
        'max_loss': None,
        'max_profit': None,
        'spread_id': None
    }

    low_distance = int(close) - low_strike
    high_distance = high_strike - int(close)
    details['strike_width'] = to_f(
        high_strike - low_strike)
    details['spread_id'] = 'S_{}_O_{}_low_{}_high_{}_w_{}'.format(
        trade_type,
        spread_type,
        option_type,
        low_distance,
        high_distance,
        details['strike_width'])
    details['low_bidask_mid'] = to_f(low_bid + low_ask / 2.0)
    details['high_bidask_mid'] = to_f(high_bid + high_ask / 2.0)
    details['mid_price'] = to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))
    details['nat_price'] = to_f(abs(
        details['low_bidask_mid'] - details['high_bidask_mid']))

    cost_of_contracts_at_mid_price = None
    revenue_of_contracts_at_mid_price = None

    if trade_type == TRADE_ENTRY:
        cost_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * details['mid_price'])
        revenue_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == SPREAD_VERTICAL_BULL:
            if option_type == OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
        else:  # bear
            if option_type == OPTION_CALL:  # debit spread
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price
            else:
                details['max_loss'] = cost_of_contracts_at_mid_price
                details['max_profit'] = revenue_of_contracts_at_mid_price

    else:  # trade exit calculations:
        revenue_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * details['mid_price'])
        cost_of_contracts_at_mid_price = to_f(
            100.0 * num_contracts * (
                details['strike_width'] - details['mid_price']))
        if spread_type == SPREAD_VERTICAL_BULL:
            if option_type == OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
        else:  # bear
            if option_type == OPTION_CALL:  # credit spread
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
            else:
                details['max_profit'] = revenue_of_contracts_at_mid_price
                details['max_loss'] = cost_of_contracts_at_mid_price
    # end of supported types of spreads

    details['cost'] = cost_of_contracts_at_mid_price
    details['revenue'] = revenue_of_contracts_at_mid_price

    return details
# end of build_option_spread_details


def build_entry_call_spread_details(
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_entry_call_spread_details

    Calculate pricing information for
    buying into `Vertical Bull Call Option Spread` contracts

    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    spread_details = build_option_spread_details(
        trade_type=TRADE_ENTRY,
        spread_type=SPREAD_VERTICAL_BULL,
        option_type=OPTION_CALL,
        close=close,
        num_contracts=num_contracts,
        low_strike=low_strike,
        low_ask=low_ask,
        low_bid=low_bid,
        high_strike=high_strike,
        high_ask=high_ask,
        high_bid=high_bid)
    return spread_details
# end of build_entry_call_spread_details


def build_exit_call_spread_details(
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_exit_call_spread_details

    Calculate pricing information for
    selling (closing-out) `Vertical Bull Call Option Spread` contracts

    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    spread_details = build_option_spread_details(
        trade_type=TRADE_EXIT,
        spread_type=SPREAD_VERTICAL_BULL,
        option_type=OPTION_CALL,
        close=close,
        num_contracts=num_contracts,
        low_strike=low_strike,
        low_ask=low_ask,
        low_bid=low_bid,
        high_strike=high_strike,
        high_ask=high_ask,
        high_bid=high_bid)
    return spread_details
# end of build_exit_call_spread_details


def build_entry_put_spread_details(
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_entry_put_spread_details

    Calculate pricing information for
    buying into `Vertical Bear Put Option Spread` contracts

    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    spread_details = build_option_spread_details(
        trade_type=TRADE_ENTRY,
        spread_type=SPREAD_VERTICAL_BEAR,
        option_type=OPTION_PUT,
        close=close,
        num_contracts=num_contracts,
        low_strike=low_strike,
        low_ask=low_ask,
        low_bid=low_bid,
        high_strike=high_strike,
        high_ask=high_ask,
        high_bid=high_bid)
    return spread_details
# end of build_entry_put_spread_details


def build_exit_put_spread_details(
        close,
        num_contracts,
        low_strike,
        low_ask,
        low_bid,
        high_strike,
        high_ask,
        high_bid):
    """build_exit_put_spread_details

    Calculate pricing information for
    selling (closing-out) `Vertical Bear Put Option Spread` contracts

    :param num_contracts: integer number of contracts
    :param low_strike: float - strike for
        the low leg of the spread
    :param low_ask: float - ask price for
        the low leg of the spread
    :param low_bid: float - bid price for
        the low leg of the spread
    :param high_strike: float - strike  for
        the high leg of the spread
    :param high_ask: float - ask price for
        the high leg of the spread
    :param high_bid: float - bid price for
        the high leg of the spread
    """

    spread_details = build_option_spread_details(
        trade_type=TRADE_EXIT,
        spread_type=SPREAD_VERTICAL_BEAR,
        option_type=OPTION_PUT,
        close=close,
        num_contracts=num_contracts,
        low_strike=low_strike,
        low_ask=low_ask,
        low_bid=low_bid,
        high_strike=high_strike,
        high_ask=high_ask,
        high_bid=high_bid)
    return spread_details
# end of build_exit_put_spread_details


def build_buy_order(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        details,
        use_key,
        shares=None,
        version=1,
        auto_fill=True,
        reason=None):
    """build_buy_order

    Create an algorithm buy order as a dictionary

    :param ticker: ticker
    :param num_owned: integer current owned
        number of shares for this asset
    :param close: float closing price of the asset
    :param balance: float amount of available capital
    :param commission: float for commission costs
    :param date: string trade date for that row usually
        ``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param details: dictionary for full row of values to review
        all buys after the algorithm finishes. (usually ``row.to_json()``)
    :param use_key: string for redis and s3 publishing of the algorithm
        result dictionary as a json-serialized dictionary
    :param shares: optional - integer number of shares to buy
        if None buy max number of shares at the ``close`` with the
        available ``balance`` amount.
    :param version: optional - version tracking integer
    :param auto_fill: optional - bool for not assuming the trade
        filled (default ``True``)
    :param reason: optional - string for recording why the algo
        decided to buy for review after the algorithm finishes
    """
    status = TRADE_OPEN
    s3_bucket_name = ALGO_BUYS_S3_BUCKET_NAME
    s3_key = use_key
    redis_key = use_key
    s3_enabled = True
    redis_enabled = True

    cost_of_trade = None
    new_shares = num_owned
    new_balance = balance
    created_date = None

    tradable_funds = balance - (2.0 * commission)

    if close > 0.1 and tradable_funds > 10.0:
        can_buy_num_shares = shares
        if not can_buy_num_shares:
            can_buy_num_shares = int(tradable_funds / close)
        cost_of_trade = to_f(
            val=(can_buy_num_shares * close) + commission)
        if can_buy_num_shares > 0:
            if cost_of_trade > balance:
                status = TRADE_NOT_ENOUGH_FUNDS
            else:
                created_date = utc_now_str()
                if auto_fill:
                    new_shares = num_owned + can_buy_num_shares
                    new_balance = balance - cost_of_trade
                    status = TRADE_FILLED
                else:
                    new_shares = shares
                    new_balance = balance
        else:
            status = TRADE_NOT_ENOUGH_FUNDS
    else:
        status = TRADE_NOT_ENOUGH_FUNDS

    order_dict = {
        'ticker': ticker,
        'status': status,
        'balance': new_balance,
        'shares': new_shares,
        'buy_price': cost_of_trade,
        'prev_balance': balance,
        'prev_shares': num_owned,
        'close': close,
        'details': details,
        'reason': reason,
        'date': date,
        'created': created_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'version': version
    }
    return order_dict
# end of build_buy_order


def build_sell_order(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        details,
        use_key,
        shares=None,
        version=1,
        auto_fill=True,
        reason=None):
    """build_sell_order

    Create an algorithm sell order as a dictionary

    :param ticker: ticker
    :param num_owned: integer current owned
        number of shares for this asset
    :param close: float closing price of the asset
    :param balance: float amount of available capital
    :param commission: float for commission costs
    :param date: string trade date for that row usually
        ``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param details: dictionary for full row of values to review
        all sells after the algorithm finishes. (usually ``row.to_json()``)
    :param use_key: string for redis and s3 publishing of the algorithm
        result dictionary as a json-serialized dictionary
    :param shares: optional - integer number of shares to sell
        if None sell all ``num_owned`` shares at the ``close``.
    :param version: optional - version tracking integer
    :param auto_fill: optional - bool for not assuming the trade
        filled (default ``True``)
    :param reason: optional - string for recording why the algo
        decided to sell for review after the algorithm finishes
    """
    status = TRADE_OPEN
    s3_bucket_name = ALGO_SELLS_S3_BUCKET_NAME
    s3_key = use_key
    redis_key = use_key
    s3_enabled = True
    redis_enabled = True

    cost_of_trade = None
    sell_price = 0.0
    new_shares = num_owned
    new_balance = balance
    created_date = None

    tradable_funds = balance - commission

    if num_owned == 0:
        status = TRADE_NO_SHARES_TO_SELL
    elif close > 0.1 and tradable_funds > 10.0:
        cost_of_trade = commission
        if shares:
            if shares > num_owned:
                shares = num_owned
        else:
            shares = num_owned
        sell_price = to_f(
            val=(shares * close) + commission)
        if cost_of_trade > balance:
            status = TRADE_NOT_ENOUGH_FUNDS
        else:
            created_date = utc_now_str()
            if auto_fill:
                new_shares = num_owned - shares
                new_balance = to_f(balance + sell_price)
                status = TRADE_FILLED
            else:
                new_shares = shares
                new_balance = balance
    else:
        status = TRADE_NOT_ENOUGH_FUNDS

    order_dict = {
        'ticker': ticker,
        'status': status,
        'balance': new_balance,
        'shares': new_shares,
        'sell_price': sell_price,
        'prev_balance': balance,
        'prev_shares': num_owned,
        'close': close,
        'details': details,
        'reason': reason,
        'date': date,
        'created': created_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled,
        'version': version
    }
    return order_dict
# end of build_sell_order


def build_trade_history_entry(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        trade_type,
        algo_start_price,
        original_balance,
        high=None,
        low=None,
        open_val=None,
        volume=None,
        ask=None,
        bid=None,
        stop_loss=None,
        trailing_stop_loss=None,
        buy_hold_units=None,
        sell_hold_units=None,
        spread_exp_date=None,
        spread_id=None,
        low_strike=None,
        low_bid=None,
        low_ask=None,
        low_volume=None,
        low_open_int=None,
        low_delta=None,
        low_gamma=None,
        low_theta=None,
        low_vega=None,
        low_rho=None,
        low_impl_vol=None,
        low_intrinsic=None,
        low_extrinsic=None,
        low_theo_price=None,
        low_theo_volatility=None,
        low_max_covered=None,
        low_exp_date=None,
        high_strike=None,
        high_bid=None,
        high_ask=None,
        high_volume=None,
        high_open_int=None,
        high_delta=None,
        high_gamma=None,
        high_theta=None,
        high_vega=None,
        high_rho=None,
        high_impl_vol=None,
        high_intrinsic=None,
        high_extrinsic=None,
        high_theo_price=None,
        high_theo_volatility=None,
        high_max_covered=None,
        high_exp_date=None,
        prev_balance=None,
        prev_num_owned=None,
        total_buys=None,
        total_sells=None,
        buy_triggered=None,
        buy_strength=None,
        buy_risk=None,
        sell_triggered=None,
        sell_strength=None,
        sell_risk=None,
        ds_id=None,
        note=None,
        err=None,
        entry_spread_dict=None,
        version=1):
    """build_trade_history_entry

    Build a dictionary for tracking an algorithm profitability per ticker
    and for ``TRADE_SHARES``, ``TRADE_VERTICAL_BULL_SPREAD``, or
    ``TRADE_VERTICAL_BEAR_SPREAD`` trading types.

    :param ticker: string ticker or symbol
    :param num_owned: integer current owned
        number of ``shares`` for this asset or number of
        currently owned ``contracts`` for an options
        spread.
    :param close: float ``close`` price of the
        underlying asset
    :param balance: float amount of available capital
    :param commission: float for commission costs
    :param date: string trade date for that row usually
        ``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``) or
        ``COMMON_TICK_DATE_FORMAT`` (``YYYY-MM-DD HH:MM:SS``)
    :param trade_type: type of the trade - supported values:
            ``TRADE_SHARES``,
            ``TRADE_VERTICAL_BULL_SPREAD``,
            ``TRADE_VERTICAL_BEAR_SPREAD``
    :param algo_start_price: float starting close/contract price
        for this algo
    :param original_balance: float starting original account
        balance for this algo
    :param high: optional - float underlying stock asset ``high`` price
    :param low: optional - float underlying stock asset ``low`` price
    :param open_val: optional - float underlying stock asset ``open`` price
    :param volume: optional - integer underlying stock asset ``volume``
    :param ask: optional - float ``ask`` price of the
        stock (for buying ``shares``)
    :param bid: optional - float ``bid`` price of the
        stock (for selling ``shares``)
    :param stop_loss: optional - float ``stop_loss`` price of the
        stock/spread (for selling ``shares`` vs ``contracts``)
    :param trailing_stop_loss: optional - float ``trailing_stop_loss``
        price of the stock/spread (for selling ``shares`` vs ``contracts``)
    :param buy_hold_units: optional - number of units
        to hold buys - helps with algorithm tuning
    :param sell_hold_units: optional - number of units
        to hold sells - helps with algorithm tuning
    :param spread_exp_date: optional - string spread contract
        expiration date (``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param spread_id: optional - spread identifier for reviewing
        spread performances
    :param low_strike: optional
        - only for vertical bull/bear trade types
        ``low leg strike price`` of the spread
    :param low_bid: optional
        - only for vertical bull/bear trade types
        ``low leg bid`` of the spread
    :param low_ask: optional
        - only for vertical bull/bear trade types
        ``low leg ask`` of the spread
    :param low_volume: optional
        - only for vertical bull/bear trade types
        ``low leg volume`` of the spread
    :param low_open_int: optional
        - only for vertical bull/bear trade types
        ``low leg open interest`` of the spread
    :param low_delta: optional
        - only for vertical bull/bear trade types
        ``low leg delta`` of the spread
    :param low_gamma: optional
        - only for vertical bull/bear trade types
        ``low leg gamma`` of the spread
    :param low_theta: optional
        - only for vertical bull/bear trade types
        ``low leg theta`` of the spread
    :param low_vega: optional
        - only for vertical bull/bear trade types
        ``low leg vega`` of the spread
    :param low_rho: optional
        - only for vertical bull/bear trade types
        ``low leg rho`` of the spread
    :param low_impl_vol: optional
        - only for vertical bull/bear trade types
        ``low leg implied volatility`` of the spread
    :param low_intrinsic: optional
        - only for vertical bull/bear trade types
        ``low leg intrinsic`` of the spread
    :param low_extrinsic: optional
        - only for vertical bull/bear trade types
        ``low leg extrinsic`` of the spread
    :param low_theo_price: optional
        - only for vertical bull/bear trade types
        ``low leg theoretical price`` of the spread
    :param low_theo_volatility: optional
        - only for vertical bull/bear trade types
        ``low leg theoretical volatility`` of the spread
    :param low_max_covered: optional
        - only for vertical bull/bear trade types
        ``low leg max covered returns`` of the spread
    :param low_exp_date: optional
        - only for vertical bull/bear trade types
        ``low leg expiration date`` of the spread
    :param high_strike: optional
        - only for vertical bull/bear trade types
        ``high leg strike price`` of the spread
    :param high_bid: optional
        - only for vertical bull/bear trade types
        ``high leg bid`` of the spread
    :param high_ask: optional
        - only for vertical bull/bear trade types
        ``high leg ask`` of the spread
    :param high_volume: optional
        - only for vertical bull/bear trade types
        ``high leg volume`` of the spread
    :param high_open_int: optional
        - only for vertical bull/bear trade types
        ``high leg open interest`` of the spread
    :param high_delta: optional
        - only for vertical bull/bear trade types
        ``high leg delta`` of the spread
    :param high_gamma: optional
        - only for vertical bull/bear trade types
        ``high leg gamma`` of the spread
    :param high_theta: optional
        - only for vertical bull/bear trade types
        ``high leg theta`` of the spread
    :param high_vega: optional
        - only for vertical bull/bear trade types
        ``high leg vega`` of the spread
    :param high_rho: optional
        - only for vertical bull/bear trade types
        ``high leg rho`` of the spread
    :param high_impl_vol: optional
        - only for vertical bull/bear trade types
        ``high leg implied volatility`` of the spread
    :param high_intrinsic: optional
        - only for vertical bull/bear trade types
        ``high leg intrinsic`` of the spread
    :param high_extrinsic: optional
        - only for vertical bull/bear trade types
        ``high leg extrinsic`` of the spread
    :param high_theo_price: optional
        - only for vertical bull/bear trade types
        ``high leg theoretical price`` of the spread
    :param high_theo_volatility: optional
        - only for vertical bull/bear trade types
        ``high leg theoretical volatility`` of the spread
    :param high_max_covered: optional
        - only for vertical bull/bear trade types
        ``high leg max covered returns`` of the spread
    :param high_exp_date: optional
        - only for vertical bull/bear trade types
        ``high leg expiration date`` of the spread
    :param prev_balance: optional - previous balance
        for this algo
    :param prev_num_owned: optional - previous num of
        ``shares`` or ``contracts``
    :param total_buys: optional - total buy orders
        for this algo
    :param total_sells: optional - total sell orders
        for this algo
    :param buy_triggered: optional - bool
        ``buy`` conditions in the algorithm triggered
    :param buy_strength: optional - float
        custom strength/confidence rating for tuning
        algorithm performance for desirable
        sensitivity and specificity
    :param buy_risk: optional - float
        custom risk rating for tuning algorithm
        peformance for avoiding custom risk for buy
        conditions
    :param sell_triggered: optional - bool
        ``sell`` conditions in the algorithm triggered
    :param sell_strength: optional - float
        custom strength/confidence rating for tuning
        algorithm performance for desirable
        sensitivity and specificity
    :param sell_risk: optional - float
        custom risk rating for tuning algorithm
        peformance for avoiding custom risk for buy
        conditions
    :param ds_id: optional - datset id for debugging
    :param note: optional - string for tracking high level
        testing notes on algorithm indicator ratings and
        internal message passing during an algorithms's
        ``self.process`` method
    :param err: optional - string for tracking errors
    :param entry_spread_dict: optional - on exit spreads
        the calculation of net gain can use the entry
        spread to determine specific performance metrics
        (work in progress)
    :param version: optional - version tracking order history
    """
    status = NOT_RUN
    algo_status = NOT_RUN
    err = None
    net_gain = 0.0
    balance_net_gain = 0.0
    breakeven_price = None
    max_profit = None  # only for option spreads
    max_loss = None  # only for option spreads
    exp_date = None  # only for option spreads

    # latest price - start price of the algo
    price_change_since_start = close - algo_start_price

    history_dict = {
        'ticker': ticker,
        'algo_start_price': algo_start_price,
        'algo_price_change': price_change_since_start,
        'original_balance': original_balance,
        'status': status,
        'algo_status': algo_status,
        'ds_id': ds_id,
        'num_owned': num_owned,
        'close': close,
        'balance': balance,
        'commission': commission,
        'date': date,
        'trade_type': trade_type,
        'high': high,
        'low': low,
        'open': open_val,
        'volume': volume,
        'ask': ask,
        'bid': bid,
        'stop_loss': stop_loss,
        'trailing_stop_loss': trailing_stop_loss,
        'buy_hold_units': buy_hold_units,
        'sell_hold_units': sell_hold_units,
        'low_strike': low_strike,
        'low_bid': low_bid,
        'low_ask': low_ask,
        'low_volume': low_volume,
        'low_open_int': low_open_int,
        'low_delta': low_delta,
        'low_gamma': low_gamma,
        'low_theta': low_theta,
        'low_vega': low_vega,
        'low_rho': low_rho,
        'low_impl_vol': low_impl_vol,
        'low_intrinsic': low_intrinsic,
        'low_extrinsic': low_extrinsic,
        'low_theo_price': low_theo_price,
        'low_theo_volatility': low_theo_volatility,
        'low_max_covered': low_max_covered,
        'low_exp_date': low_exp_date,
        'high_strike': high_strike,
        'high_bid': high_bid,
        'high_ask': high_ask,
        'high_volume': high_volume,
        'high_open_int': high_open_int,
        'high_delta': high_delta,
        'high_gamma': high_gamma,
        'high_theta': high_theta,
        'high_vega': high_vega,
        'high_rho': high_rho,
        'high_impl_vol': high_impl_vol,
        'high_intrinsic': high_intrinsic,
        'high_extrinsic': high_extrinsic,
        'high_theo_price': high_theo_price,
        'high_theo_volatility': high_theo_volatility,
        'high_max_covered': high_max_covered,
        'high_exp_date': high_exp_date,
        'spread_id': spread_id,
        'net_gain': net_gain,
        'breakeven_price': breakeven_price,
        'max_profit': max_profit,
        'max_loss': max_loss,
        'exp_date': exp_date,
        'prev_balance': prev_balance,
        'prev_num_owned': prev_num_owned,
        'total_buys': total_buys,
        'total_sells': total_sells,
        'note': note,
        'err': err,
        'version': version
    }

    # evaluate if the algorithm is gaining
    # cash over the test
    if balance and original_balance:
        # net change on the balance
        # note this needs to be upgraded to
        # support orders per ticker
        # single tickers will work for v1
        balance_net_gain = balance - original_balance
        if balance_net_gain > 0.0:
            algo_status = ALGO_PROFITABLE
        else:
            algo_status = ALGO_NOT_PROFITABLE
    else:
        history_dict['err'] = (
            '{} ds_id={} missing balance={} and '
            'original_balance={}'.format(
                ticker,
                ds_id,
                balance,
                original_balance))
        algo_status = ALGO_ERROR
    # if starting balance and original_balance exist
    # to determine algorithm trade profitability

    # if there are no shares to sell then
    # there's no current trade open
    if num_owned and num_owned < 1:
        status = TRADE_NO_SHARES_TO_SELL
    else:
        if close < 0.01:
            history_dict['err'] = (
                '{} ds_id={} close={} must be greater '
                'than 0.01'.format(
                    ticker,
                    ds_id,
                    close))
            status = TRADE_ERROR
        elif algo_start_price < 0.01:
            history_dict['err'] = (
                '{} ds_id={} algo_start_price={} must be greater '
                'than 0.01'.format(
                    ticker,
                    ds_id,
                    algo_start_price))
            status = TRADE_ERROR
        else:
            price_net_gain = close - algo_start_price
            if price_net_gain > 0.0:
                status = TRADE_PROFITABLE
            else:
                status = TRADE_NOT_PROFITABLE
    # if starting price when algo started and close exist
    # determine if this trade profitability

    # Assign calculated values:
    history_dict['net_gain'] = net_gain
    history_dict['balance_net_gain'] = balance_net_gain
    history_dict['breakeven_price'] = breakeven_price
    history_dict['max_profit'] = max_profit
    history_dict['max_loss'] = max_loss
    history_dict['exp_date'] = exp_date

    # assign statuses
    history_dict['status'] = status
    history_dict['algo_status'] = algo_status

    return history_dict
# end of build_trade_history_entry
