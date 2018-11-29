"""
Build a dictionary for running an algorithm
"""

import datetime
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_algo_request(
        ticker=None,
        tickers=None,
        use_key=None,
        start_date=None,
        end_date=None,
        datasets=None,
        balance=None,
        commission=None,
        num_shares=None,
        config_file=None,
        config_dict=None,
        load_config=None,
        history_config=None,
        report_config=None,
        extract_config=None,
        timeseries=None,
        trade_strategy=None,
        cache_freq='daily',
        label='algo'):
    """build_algo_request

    Create a dictionary for building an algorithm. This is
    opinionated to how the underlying date-based caching
    strategy is running per day. Each business day becomes
    a possible dataset to process with an algorithm.

    :param ticker: ticker
    :param tickers: optional - list of tickers
    :param use_key: redis and s3 to store the algo result
    :param start_date: string date format ``YYYY-MM-DD HH:MM:SS``
    :param end_date: string date format ``YYYY-MM-DD HH:MM:SS``
    :param datasets: list of string dataset types
    :param balance: starting capital balance
    :param commission: commission for buy or sell
    :param num_shares: optional - integer number of starting shares
    :param cache_freq: optional - cache frequency
        (``daily`` is default)
    :param label: optional - algo log tracking name
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

    **Algorithm Dataset Extraction, Loading and Publishing arguments**

    :param load_config: optional - dictionary
        for setting member variables to load an
        agorithm-ready dataset from
        a file, s3 or redis
    :param history_config: optional - dictionary
        for setting member variables to publish
        an algo ``trade history`` to s3, redis, a file
        or slack
    :param report_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack
    :param extract_config: optional - dictionary
        for setting member variables to publish
        an algo ``trading performance report`` to s3,
        redis, a file or slack

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

    s3_bucket_name = ae_consts.ALGO_RESULT_S3_BUCKET_NAME
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
        'config_file': config_file,
        'config_dict': config_dict,
        'balance': balance,
        'commission': commission,
        'load_config': load_config,
        'history_config': history_config,
        'report_config': report_config,
        'extract_config': extract_config,
        'start_date': None,
        'end_date': None,
        'timeseries': timeseries,
        'trade_strategy': trade_strategy,
        'version': 1,
        'label': label
    }

    start_date_val = ae_utils.get_date_from_str(start_date)
    end_date_val = ae_utils.get_date_from_str(end_date)
    if start_date_val > end_date_val:
        raise Exception(
            'Invalid start_date={} must be less than end_date={}'.format(
                start_date,
                end_date))

    use_dates = []
    new_dataset = None
    cur_date = start_date_val
    if not work['start_date']:
        work['start_date'] = start_date_val.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
    if not work['end_date']:
        work['end_date'] = end_date_val.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT)
    while cur_date <= end_date_val:
        if cur_date.weekday() < 5:
            for t in use_tickers:
                if cache_freq == 'daily':
                    new_dataset = '{}_{}'.format(
                        t,
                        cur_date.strftime(
                            ae_consts.COMMON_DATE_FORMAT))
                else:
                    new_dataset = '{}_{}'.format(
                        t,
                        cur_date.strftime(
                            ae_consts.COMMON_TICK_DATE_FORMAT))
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

    if len(use_dates) > 0:
        work['extract_datasets'] = use_dates

        log.debug(
            'tickers={} balance={} start={} end={} '
            'cache_freq={} request={}'.format(
                work['tickers'],
                work['balance'],
                work['extract_datasets'][0],
                work['extract_datasets'][-1],
                cache_freq,
                ae_consts.ppj(work)))
    else:
        log.error(
            'there are not enough dates to test between start={} end={} '
            'tickers={} request={}'.format(
                start_date_val,
                end_date_val,
                work['tickers'],
                cache_freq,
                ae_consts.ppj(work)))

    return work
# end of build_algo_request
