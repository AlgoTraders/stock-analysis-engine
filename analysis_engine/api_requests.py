"""
Helpers and examples for supported API Requests that each Celery
Task supports:

- analysis_engine.work_tasks.get_new_pricing_data
- analysis_engine.work_tasks.handle_pricing_update_task
- analysis_engine.work_tasks.publish_pricing_update

"""

import datetime
import analysis_engine.iex.utils as iex_utils
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import DAILY_S3_BUCKET_NAME
from analysis_engine.consts import MINUTE_S3_BUCKET_NAME
from analysis_engine.consts import TICK_S3_BUCKET_NAME
from analysis_engine.consts import STATS_S3_BUCKET_NAME
from analysis_engine.consts import PEERS_S3_BUCKET_NAME
from analysis_engine.consts import NEWS_S3_BUCKET_NAME
from analysis_engine.consts import FINANCIALS_S3_BUCKET_NAME
from analysis_engine.consts import EARNINGS_S3_BUCKET_NAME
from analysis_engine.consts import DIVIDENDS_S3_BUCKET_NAME
from analysis_engine.consts import COMPANY_S3_BUCKET_NAME
from analysis_engine.consts import PREPARE_S3_BUCKET_NAME
from analysis_engine.consts import ANALYZE_S3_BUCKET_NAME
from analysis_engine.iex.consts import FETCH_DAILY
from analysis_engine.iex.consts import FETCH_MINUTE
from analysis_engine.iex.consts import FETCH_TICK
from analysis_engine.iex.consts import FETCH_STATS
from analysis_engine.iex.consts import FETCH_PEERS
from analysis_engine.iex.consts import FETCH_NEWS
from analysis_engine.iex.consts import FETCH_FINANCIALS
from analysis_engine.iex.consts import FETCH_EARNINGS
from analysis_engine.iex.consts import FETCH_DIVIDENDS
from analysis_engine.iex.consts import FETCH_COMPANY
from analysis_engine.iex.consts import DATAFEED_DAILY
from analysis_engine.iex.consts import DATAFEED_MINUTE
from analysis_engine.iex.consts import DATAFEED_TICK
from analysis_engine.iex.consts import DATAFEED_STATS
from analysis_engine.iex.consts import DATAFEED_PEERS
from analysis_engine.iex.consts import DATAFEED_NEWS
from analysis_engine.iex.consts import DATAFEED_FINANCIALS
from analysis_engine.iex.consts import DATAFEED_EARNINGS
from analysis_engine.iex.consts import DATAFEED_DIVIDENDS
from analysis_engine.iex.consts import DATAFEED_COMPANY


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
    s3_bucket_name = 'pricing'
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
    cache_data = {
        "news": [
            {
                "d": "16 hours ago",
                "s": "Yahoo Finance",
                "sp": "Some Title 1",
                "sru": "http://news.google.com/news/url?values",
                "t": "Some Title 1",
                "tt": "1493311950",
                "u": "http://finance.yahoo.com/news/url1",
                "usg": "ke1"
            },
            {
                "d": "18 hours ago",
                "s": "Yahoo Finance",
                "sp": "Some Title 2",
                "sru": "http://news.google.com/news/url?values",
                "t": "Some Title 2",
                "tt": "1493311950",
                "u": "http://finance.yahoo.com/news/url2",
                "usg": "key2"
            }
        ],
        "options": [
            {
                "ask": 0.0,
                "bid": 0.0,
                "change": 0.0,
                "contractSize": "REGULAR",
                "contractSymbol": "SPY170505C00015000",
                "currency": "USD",
                "expiration": 1493942400,
                "impliedVolatility": 0.2500075,
                "inTheMoney": False,
                "lastPrice": 0.28,
                "lastTradeDate": 1493323145,
                "openInterest": 0,
                "percentChange": 0.0,
                "strike": 286.0,
                "volume": 1106
            }
        ],
        "pricing": {
            "ask": 0.0,
            "askSize": 8,
            "averageDailyVolume10Day": 67116380,
            "averageDailyVolume3Month": 64572187,
            "bid": 0.0,
            "bidSize": 10,
            "close": 287.6,
            "currency": "USD",
            "esgPopulated": False,
            "exchange": "PCX",
            "exchangeDataDelayedBy": 0,
            "exchangeTimezoneName": "America/New_York",
            "exchangeTimezoneShortName": "EDT",
            "fiftyDayAverage": 285.21735,
            "fiftyDayAverageChange": 2.8726501,
            "fiftyDayAverageChangePercent": 0.010071794,
            "fiftyTwoWeekHigh": 291.74,
            "fiftyTwoWeekHighChange": -3.649994,
            "fiftyTwoWeekHighChangePercent": -0.012511119,
            "fiftyTwoWeekLow": 248.02,
            "fiftyTwoWeekLowChange": 40.069992,
            "fiftyTwoWeekLowChangePercent": 0.16155952,
            "fiftyTwoWeekRange": "248.02 - 291.74",
            "financialCurrency": "USD",
            "fullExchangeName": "NYSEArca",
            "gmtOffSetMilliseconds": -14400000,
            "high": 289.03,
            "language": "en-US",
            "longName": "SPDR S&amp;P 500 ETF",
            "low": 287.88,
            "market": "us_market",
            "marketCap": 272023797760,
            "marketState": "POSTPOST",
            "messageBoardId": "finmb_6160262",
            "open": 288.74,
            "postMarketChange": 0.19998169,
            "postMarketChangePercent": 0.06941398,
            "postMarketPrice": 288.3,
            "postMarketTime": 1536623987,
            "priceHint": 2,
            "quoteSourceName": "Delayed Quote",
            "quoteType": "ETF",
            "region": "US",
            "regularMarketChange": 0.48999023,
            "regularMarketChangePercent": 0.17037213,
            "regularMarketDayHigh": 289.03,
            "regularMarketDayLow": 287.88,
            "regularMarketDayRange": "287.88 - 289.03",
            "regularMarketOpen": 288.74,
            "regularMarketPreviousClose": 287.6,
            "regularMarketPrice": 288.09,
            "regularMarketTime": 1536609602,
            "regularMarketVolume": 50210903,
            "sharesOutstanding": 944232000,
            "shortName": "SPDR S&P 500",
            "sourceInterval": 15,
            "symbol": "SPY",
            "tradeable": True,
            "trailingThreeMonthNavReturns": 7.71,
            "trailingThreeMonthReturns": 7.63,
            "twoHundredDayAverage": 274.66153,
            "twoHundredDayAverageChange": 13.428467,
            "twoHundredDayAverageChangePercent": 0.048890963,
            "volume": 50210903,
            "ytdReturn": 9.84
        }
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
    s3_bucket_name = 'pricing'
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
    s3_bucket_name = 'pricing'
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
    s3_bucket_name = 'pricing'
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

    Fetch minute data from IEX

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


def build_iex_fetch_tick_request(
        label=None):
    """build_iex_fetch_tick_request

    Fetch tick data from IEX

    :param label: log label to use
    """
    ticker = TICKER
    base_key = '{}_tick_{}'.format(
        ticker,
        datetime.datetime.utcnow().strftime(
            '%Y_%m_%d_%H_%M_%S'))
    s3_bucket_name = TICK_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': FETCH_TICK,
        'fd_type': DATAFEED_TICK,
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
# end of build_iex_fetch_tick_request


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
