"""
Helpers and examples for supported API Requests that each Celery
Task supports:

- analysis_engine.work_tasks.get_new_pricing_data
- analysis_engine.work_tasks.handle_pricing_update_task
- analysis_engine.work_tasks.publish_pricing_update

"""

import datetime
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.iex.consts as iex_consts
import analysis_engine.td.consts as td_consts
import analysis_engine.options_dates as opt_dates


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
        last_str = ae_utils.get_last_close_str(
            fmt=ae_consts.COMMON_DATE_FORMAT)
        use_base_key = f'{ticker}_{last_str}'

    date_str = ae_utils.utc_date_str(
        fmt=ae_consts.COMMON_DATE_FORMAT)
    now_str = ae_utils.utc_now_str(
        fmt=ae_consts.COMMON_TICK_DATE_FORMAT)

    daily_redis_key = (
        f'{use_base_key}_{ae_consts.DAILY_S3_BUCKET_NAME}')
    minute_redis_key = (
        f'{use_base_key}_{ae_consts.MINUTE_S3_BUCKET_NAME}')
    quote_redis_key = (
        f'{use_base_key}_{ae_consts.QUOTE_S3_BUCKET_NAME}')
    stats_redis_key = (
        f'{use_base_key}_{ae_consts.STATS_S3_BUCKET_NAME}')
    peers_redis_key = (
        f'{use_base_key}_{ae_consts.PEERS_S3_BUCKET_NAME}')
    news_iex_redis_key = (
        f'{use_base_key}_{ae_consts.NEWS_S3_BUCKET_NAME}1')
    financials_redis_key = (
        f'{use_base_key}_{ae_consts.FINANCIALS_S3_BUCKET_NAME}')
    earnings_redis_key = (
        f'{use_base_key}_{ae_consts.EARNINGS_S3_BUCKET_NAME}')
    dividends_redis_key = (
        f'{use_base_key}_{ae_consts.DIVIDENDS_S3_BUCKET_NAME}')
    company_redis_key = (
        f'{use_base_key}_{ae_consts.COMPANY_S3_BUCKET_NAME}')
    options_yahoo_redis_key = (
        f'{use_base_key}_{ae_consts.OPTIONS_S3_BUCKET_NAME}')
    call_options_yahoo_redis_key = (
        f'{use_base_key}_calls')
    put_options_yahoo_redis_key = (
        f'{use_base_key}_puts')
    pricing_yahoo_redis_key = (
        f'{use_base_key}_{ae_consts.PRICING_S3_BUCKET_NAME}')
    news_yahoo_redis_key = (
        f'{use_base_key}_{ae_consts.NEWS_S3_BUCKET_NAME}')
    call_options_td_redis_key = (
        f'{use_base_key}_tdcalls')
    put_options_td_redis_key = (
        f'{use_base_key}_tdputs')

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
        'calls': call_options_yahoo_redis_key,
        'puts': put_options_yahoo_redis_key,
        'pricing': pricing_yahoo_redis_key,
        'news': news_yahoo_redis_key,
        'tdcalls': call_options_td_redis_key,
        'tdputs': put_options_td_redis_key,
        'ticker': ticker,
        'ds_id': ds_id,
        'label': label,
        'created': now_str,
        'date': date_str,
        'manifest_key': use_base_key,
        'version': ae_consts.CACHE_DICT_VERSION
    }

    # set keys/values for redis/minio from the
    # service_dict - helper method for
    # launching job chains
    if service_dict:
        for k in ae_consts.SERVICE_VALS:
            if k in service_dict:
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    base_key = f'''{ticker}_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.S3_BUCKET
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    base_key = f'''{ticker}_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.S3_BUCKET
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
        'df_compress': True,
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    base_key = f'''{ticker}_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.S3_BUCKET
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    s3_bucket_name = ae_consts.S3_BUCKET
    s3_compiled_bucket_name = ae_consts.S3_COMPILED_BUCKET
    s3_key = f'{ticker}_latest'
    redis_key = f'{ticker}_latest'
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    base_key = f'''{ticker}_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.S3_BUCKET
    s3_key = base_key
    redis_key = base_key
    s3_prepared_bucket_name = ae_consts.PREPARE_S3_BUCKET_NAME
    s3_prepared_key = f'{base_key}.csv'
    redis_prepared_key = f'{base_key}'
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
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    base_key = f'''{ticker}_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.PREPARE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_analyzed_bucket_name = ae_consts.ANALYZE_S3_BUCKET_NAME
    s3_analyzed_key = f'{base_key}.csv'
    redis_analyzed_key = f'{base_key}'
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

    Fetch `daily
    data <https://iexcloud.io/docs/api/#historical-prices>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_daily_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.DAILY_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_DAILY,
        'fd_type': iex_consts.DATAFEED_DAILY,
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

    Fetch `minute
    data <https://iexcloud.io/docs/api/#historical-prices>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_minute_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.MINUTE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_MINUTE,
        'fd_type': iex_consts.DATAFEED_MINUTE,
        'ticker': ticker,
        'timeframe': '1d',
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

    Fetch `quote
    data <https://iexcloud.io/docs/api/#quote>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_quote_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.QUOTE_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_QUOTE,
        'fd_type': iex_consts.DATAFEED_QUOTE,
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

    Fetch `stats
    data <https://iexcloud.io/docs/api/#key-stats>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_stat_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.STATS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_STATS,
        'fd_type': iex_consts.DATAFEED_STATS,
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
# end of build_iex_fetch_stats_request


def build_iex_fetch_peers_request(
        label=None):
    """build_iex_fetch_peers_request

    Fetch `peers
    data <https://iexcloud.io/docs/api/#peers>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_peer_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.PEERS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_PEERS,
        'fd_type': iex_consts.DATAFEED_PEERS,
        'ticker': ticker,
        'timeframe': '1d',
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

    Fetch `news
    data <https://iexcloud.io/docs/api/#news>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_news_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.NEWS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_NEWS,
        'fd_type': iex_consts.DATAFEED_NEWS,
        'ticker': ticker,
        'timeframe': '1d',
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

    Fetch `financials
    data <https://iexcloud.io/docs/api/#financials>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_financial_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.FINANCIALS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_FINANCIALS,
        'fd_type': iex_consts.DATAFEED_FINANCIALS,
        'ticker': ticker,
        'timeframe': '1d',
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

    Fetch `earnings
    data <https://iexcloud.io/docs/api/#earnings>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_earning_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.EARNINGS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_EARNINGS,
        'fd_type': iex_consts.DATAFEED_EARNINGS,
        'ticker': ticker,
        'timeframe': '1d',
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

    Fetch `dividends
    data <https://iexcloud.io/docs/api/#dividends>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_dividend_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.DIVIDENDS_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_DIVIDENDS,
        'fd_type': iex_consts.DATAFEED_DIVIDENDS,
        'ticker': ticker,
        'timeframe': '2y',
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

    Fetch `company
    data <https://iexcloud.io/docs/api/#company>`__
    from IEX

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_company_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = ae_consts.COMPANY_S3_BUCKET_NAME
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    work = {
        'ft_type': iex_consts.FETCH_COMPANY,
        'fd_type': iex_consts.DATAFEED_COMPANY,
        'ticker': ticker,
        'timeframe': '1d',
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
        iex_datasets=ae_consts.IEX_DATASETS_DEFAULT,
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

    s3_bucket_name = ae_consts.SCREENER_S3_BUCKET_NAME
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


"""
Tradier API Requests
"""


def build_td_fetch_calls_request(
        label=None):
    """build_td_fetch_calls_request

    Fetch tradier calls

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_tdcalls_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = 'tdcalls'
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    exp_date = opt_dates.option_expiration().strftime(
        ae_consts.COMMON_DATE_FORMAT)

    work = {
        'ft_type': td_consts.FETCH_TD_CALLS,
        'fd_type': td_consts.DATAFEED_TD_CALLS,
        'ticker': ticker,
        'exp_date': exp_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_td_fetch_calls_request


def build_td_fetch_puts_request(
        label=None):
    """build_td_fetch_puts_request

    Fetch tradier puts

    :param label: log label to use
    """
    ticker = ae_consts.TICKER
    base_key = f'''{ticker}_tdputs_{datetime.datetime.utcnow().strftime(
        '%Y_%m_%d_%H_%M_%S')}'''
    s3_bucket_name = 'tdputs'
    s3_key = base_key
    redis_key = base_key
    s3_enabled = True
    redis_enabled = True

    exp_date = opt_dates.option_expiration().strftime(
        ae_consts.COMMON_DATE_FORMAT)

    work = {
        'ft_type': td_consts.FETCH_TD_PUTS,
        'fd_type': td_consts.DATAFEED_TD_PUTS,
        'ticker': ticker,
        'exp_date': exp_date,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

    if label:
        work['label'] = label

    return work
# end of build_td_fetch_puts_request
