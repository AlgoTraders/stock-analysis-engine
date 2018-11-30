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
from analysis_engine.consts import PRICING_S3_BUCKET_NAME
from analysis_engine.consts import OPTIONS_S3_BUCKET_NAME
from analysis_engine.consts import S3_BUCKET
from analysis_engine.consts import S3_COMPILED_BUCKET
from analysis_engine.consts import SERVICE_VALS
from analysis_engine.consts import IEX_DATASETS_DEFAULT
from analysis_engine.utils import get_last_close_str
from analysis_engine.utils import utc_date_str
from analysis_engine.utils import utc_now_str
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

    daily_redis_key = '{}_{}'.format(
        use_base_key,
        DAILY_S3_BUCKET_NAME)
    minute_redis_key = '{}_{}'.format(
        use_base_key,
        MINUTE_S3_BUCKET_NAME)
    quote_redis_key = '{}_{}'.format(
        use_base_key,
        QUOTE_S3_BUCKET_NAME)
    stats_redis_key = '{}_{}'.format(
        use_base_key,
        STATS_S3_BUCKET_NAME)
    peers_redis_key = '{}_{}'.format(
        use_base_key,
        PEERS_S3_BUCKET_NAME)
    news_iex_redis_key = '{}_{}1'.format(
        use_base_key,
        NEWS_S3_BUCKET_NAME)
    financials_redis_key = '{}_{}'.format(
        use_base_key,
        FINANCIALS_S3_BUCKET_NAME)
    earnings_redis_key = '{}_{}'.format(
        use_base_key,
        EARNINGS_S3_BUCKET_NAME)
    dividends_redis_key = '{}_{}'.format(
        use_base_key,
        DIVIDENDS_S3_BUCKET_NAME)
    company_redis_key = '{}_{}'.format(
        use_base_key,
        COMPANY_S3_BUCKET_NAME)
    options_yahoo_redis_key = '{}_{}'.format(
        use_base_key,
        OPTIONS_S3_BUCKET_NAME)
    pricing_yahoo_redis_key = '{}_{}'.format(
        use_base_key,
        PRICING_S3_BUCKET_NAME)
    news_yahoo_redis_key = '{}_{}'.format(
        use_base_key,
        NEWS_S3_BUCKET_NAME)

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
