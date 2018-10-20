"""
Fetch all data for a ticker using all datafeeds
and cache it in Redis and S3 (Minio).
"""

import os
import json
import analysis_engine.build_result as build_result
import analysis_engine.work_tasks.get_new_pricing_data as price_utils
import analysis_engine.iex.extract_df_from_redis as iex_extract_utils
import analysis_engine.yahoo.extract_df_from_redis as yahoo_extract_utils
from analysis_engine.consts import get_status
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import FAILED
from analysis_engine.consts import NOT_RUN
from analysis_engine.utils import get_last_close_str
from analysis_engine.api_requests import get_ds_dict
from analysis_engine.api_requests import build_get_new_pricing_request
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def run(ticker=None,
        tickers=None,
        fetch_mode=None,
        iex_datasets=None,
        redis_enabled=True,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        s3_enabled=True,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=False,
        celery_disabled=True,
        broker_url=None,
        result_backend=None,
        label=None):
    """run

    :param ticker:
    :param tickers:
    :param fetch_mode:
    :param iex_datasets:
    :param redis_enabled:
    :param redis_address:
    :param redis_db:
    :param redis_password:
    :param redis_expire:
    :param s3_enabled:
    :param s3_address:
    :param s3_bucket:
    :param s3_access_key:
    :param s3_secret_key:
    :param s3_region_name:
    :param s3_secure:
    :param celery_disabled:
    :param broker_url:
    :param result_backend:
    :param label:
    """

    err = None
    rec = {}
    res = build_result.build_result(
        status=NOT_RUN,
        err=err,
        rec=rec)

    extract_records = []

    use_tickers = tickers
    if ticker:
        use_tickers = [ticker]
    else:
        if not use_tickers:
            use_tickers = []

    default_iex_datasets = [
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

    if not iex_datasets:
        iex_datasets = default_iex_datasets
    if not fetch_mode:
        fetch_mode = 'all'

    if redis_enabled:
        if not redis_address:
            redis_address = os.getenv(
                'REDIS_ADDRESS',
                'localhost:6379')
        if not redis_password:
            redis_password = os.getenv(
                'REDIS_PASSWORD',
                None)
        if not redis_db:
            redis_db = int(os.getenv(
                'REDIS_DB',
                '0'))
        if not redis_expire:
            redis_expire = os.getenv(
                'REDIS_EXPIRE',
                None)
    if s3_enabled:
        if not s3_address:
            s3_address = os.getenv(
                'S3_ADDRESS',
                'localhost:9000')
        if not s3_access_key:
            s3_access_key = os.getenv(
                'AWS_ACCESS_KEY_ID',
                'trexaccesskey')
        if not s3_secret_key:
            s3_secret_key = os.getenv(
                'AWS_SECRET_ACCESS_KEY',
                'trex123321')
        if not s3_region_name:
            s3_region_name = os.getenv(
                'AWS_DEFAULT_REGION',
                'us-east-1')
        if not s3_secure:
            s3_secure = os.getenv(
                'S3_SECURE',
                '0') == '1'
        if not s3_bucket:
            s3_bucket = os.getenv(
                'S3_BUCKET',
                'dev')
    if not broker_url:
        broker_url = os.getenv(
            'WORKER_BROKER_URL',
            'redis://0.0.0.0:6379/13')
    if not result_backend:
        result_backend = os.getenv(
            'WORKER_BACKEND_URL',
            'redis://0.0.0.0:6379/14')

    if not label:
        label = 'get-latest'

    num_tickers = len(use_tickers)
    last_close_str = get_last_close_str()

    if iex_datasets:
        log.info(
            '{} - getting latest for tickers={} '
            'iex={}'.format(
                label,
                num_tickers,
                json.dumps(iex_datasets)))
    else:
        log.info(
            '{} - getting latest for tickers={}'.format(
                label,
                num_tickers))

    for ticker in use_tickers:

        ticker_key = '{}_{}'.format(
            ticker,
            last_close_str)

        fetch_req = build_get_new_pricing_request()
        fetch_req['base_key'] = ticker_key
        fetch_req['celery_disabled'] = celery_disabled
        fetch_req['ticker'] = ticker
        fetch_req['label'] = label
        fetch_req['fetch_mode'] = fetch_mode
        fetch_req['iex_datasets'] = iex_datasets
        fetch_req['s3_enabled'] = s3_enabled
        fetch_req['s3_bucket'] = s3_bucket
        fetch_req['s3_address'] = s3_address
        fetch_req['s3_secure'] = s3_secure
        fetch_req['s3_region_name'] = s3_region_name
        fetch_req['s3_access_key'] = s3_access_key
        fetch_req['s3_secret_key'] = s3_secret_key
        fetch_req['s3_key'] = ticker_key
        fetch_req['redis_enabled'] = redis_enabled
        fetch_req['redis_address'] = redis_address
        fetch_req['redis_password'] = redis_password
        fetch_req['redis_db'] = redis_db
        fetch_req['redis_key'] = ticker_key
        fetch_req['redis_expire'] = redis_expire

        fetch_req['redis_address'] = redis_address
        fetch_req['s3_address'] = s3_address

        log.info(
            '{} - fetching ticker={} last_close={} '
            'redis_address={} s3_address={}'.format(
                label,
                ticker,
                last_close_str,
                fetch_req['redis_address'],
                fetch_req['s3_address']))

        fetch_res = price_utils.run_get_new_pricing_data(
            work_dict=fetch_req)
        if fetch_res['status'] == SUCCESS:
            log.info(
                '{} - fetched ticker={} '
                'preparing for extraction'.format(
                    label,
                    ticker))
            extract_req = fetch_req
            extract_records.append(extract_req)
        else:
            log.error(
                '{} - failed getting ticker={} data '
                'status={} err={}'.format(
                    label,
                    ticker,
                    get_status(status=fetch_res['status']),
                    fetch_res['err']))
        # end of if worked or not
    # end for all tickers to fetch

    """
    Extract Datasets
    """

    iex_daily_status = FAILED
    iex_minute_status = FAILED
    iex_quote_status = FAILED
    iex_stats_status = FAILED
    iex_peers_status = FAILED
    iex_news_status = FAILED
    iex_financials_status = FAILED
    iex_earnings_status = FAILED
    iex_dividends_status = FAILED
    iex_company_status = FAILED
    yahoo_news_status = FAILED
    yahoo_options_status = FAILED
    yahoo_pricing_status = FAILED

    iex_daily_df = None
    iex_minute_df = None
    iex_quote_df = None
    iex_stats_df = None
    iex_peers_df = None
    iex_news_df = None
    iex_financials_df = None
    iex_earnings_df = None
    iex_dividends_df = None
    iex_company_df = None
    yahoo_option_calls_df = None
    yahoo_option_puts_df = None
    yahoo_pricing_df = None
    yahoo_news_df = None

    rec = {
        'tickers': [],
        'ticker_dict': {}
    }

    for service_dict in extract_records:
        ticker_data = {}
        ticker = service_dict['ticker']

        extract_req = get_ds_dict(
            ticker=ticker,
            base_key=service_dict.get('base_key', None),
            ds_id=label,
            service_dict=service_dict)

        rec['tickers'].append(ticker)

        if 'daily' in iex_datasets:
            iex_daily_status, iex_daily_df = \
                iex_extract_utils.extract_daily_dataset(
                    extract_req)
            if iex_daily_status != SUCCESS:
                log.error(
                    'failed extracting iex_daily={}'.format(ticker))
        if 'minute' in iex_datasets:
            iex_minute_status, iex_minute_df = \
                iex_extract_utils.extract_minute_dataset(
                    extract_req)
            if iex_minute_status != SUCCESS:
                log.error(
                    'failed extracting iex_minute={}'.format(ticker))
        if 'quote' in iex_datasets:
            iex_quote_status, iex_quote_df = \
                iex_extract_utils.extract_quote_dataset(
                    extract_req)
            if iex_quote_status != SUCCESS:
                log.error(
                    'failed extracting iex_quote={}'.format(ticker))
        if 'stats' in iex_datasets:
            iex_stats_df, iex_stats_df = \
                iex_extract_utils.extract_stats_dataset(
                    extract_req)
            if iex_stats_status != SUCCESS:
                log.error(
                    'failed extracting iex_stats={}'.format(ticker))
        if 'peers' in iex_datasets:
            iex_peers_df, iex_peers_df = \
                iex_extract_utils.extract_peers_dataset(
                    extract_req)
            if iex_peers_status != SUCCESS:
                log.error(
                    'failed extracting iex_peers={}'.format(ticker))
        if 'news' in iex_datasets:
            iex_news_status, iex_news_df = \
                iex_extract_utils.extract_news_dataset(
                    extract_req)
            if iex_news_status != SUCCESS:
                log.error(
                    'failed extracting iex_news={}'.format(ticker))
        if 'financials' in iex_datasets:
            iex_financials_status, iex_financials_df = \
                iex_extract_utils.extract_financials_dataset(
                    extract_req)
            if iex_financials_status != SUCCESS:
                log.error(
                    'failed extracting iex_financials={}'.format(ticker))
        if 'earnings' in iex_datasets:
            iex_earnings_status, iex_earnings_df = \
                iex_extract_utils.extract_dividends_dataset(
                    extract_req)
            if iex_earnings_status != SUCCESS:
                log.error(
                    'failed extracting iex_earnings={}'.format(ticker))
        if 'dividends' in iex_datasets:
            iex_dividends_status, iex_dividends_df = \
                iex_extract_utils.extract_dividends_dataset(
                    extract_req)
            if iex_dividends_status != SUCCESS:
                log.error(
                    'failed extracting iex_dividends={}'.format(ticker))
        if 'company' in iex_datasets:
            iex_company_status, iex_company_df = \
                iex_extract_utils.extract_dividends_dataset(
                    extract_req)
            if iex_company_status != SUCCESS:
                log.error(
                    'failed extracting iex_company={}'.format(ticker))
        # end of iex extracts

        if fetch_mode in ['all', 'yahoo']:
            yahoo_options_status, yahoo_option_calls_df = \
                yahoo_extract_utils.extract_option_calls_dataset(
                    extract_req)
            yahoo_options_status, yahoo_option_puts_df = \
                yahoo_extract_utils.extract_option_puts_dataset(
                    extract_req)
            if yahoo_options_status != SUCCESS:
                log.error(
                    'failed extracting yahoo_options={}'.format(ticker))
            yahoo_pricing_status, yahoo_pricing_df = \
                yahoo_extract_utils.extract_pricing_dataset(
                    extract_req)
            if yahoo_pricing_status != SUCCESS:
                log.error(
                    'failed extracting yahoo_pricing={}'.format(ticker))
            yahoo_news_status, yahoo_news_df = \
                yahoo_extract_utils.extract_yahoo_news_dataset(
                    extract_req)
            if yahoo_news_status != SUCCESS:
                log.error(
                    'failed extracting yahoo_news={}'.format(ticker))
        # end of yahoo extracts

        ticker_data['daily'] = iex_daily_df
        ticker_data['minute'] = iex_minute_df
        ticker_data['quote'] = iex_quote_df
        ticker_data['stats'] = iex_stats_df
        ticker_data['peers'] = iex_peers_df
        ticker_data['news1'] = iex_news_df
        ticker_data['financials'] = iex_financials_df
        ticker_data['earnings'] = iex_earnings_df
        ticker_data['dividends'] = iex_dividends_df
        ticker_data['company'] = iex_company_df
        ticker_data['calls'] = yahoo_option_calls_df
        ticker_data['puts'] = yahoo_option_puts_df
        ticker_data['pricing'] = yahoo_pricing_df
        ticker_data['news'] = yahoo_news_df

        rec['ticker_dict'][ticker] = ticker_data
    # end of for service_dict in extract_records

    """
    Start Analysis
    """

    log.info(
        '{} - analyzing tickers={}'.format(
            label,
            len(rec['ticker_dict'])))

    for ticker in rec['ticker_dict']:
        log.info(ticker)
        ticker_data = rec['ticker_dict'][ticker]
        print(ticker_data)

    res = build_result.build_result(
        status=SUCCESS,
        err=err,
        rec=rec)

    return res
# end of run


def start():
    """start"""
    label = 'run'
    log.info(
        '{} - start'.format(
            label))

    """
    Input - Set up dataset sources to collect
    """

    # fetch from: 'all', 'iex' or 'yahoo'
    fetch_mode = 'iex'
    iex_datasets = [
        # 'daily',
        # 'minute',
        # 'quote',
        # 'stats',
        # 'peers',
        # 'news',
        'financials',
        # 'earnings',
        # 'dividends'
        # 'company'
    ]

    """
    Input - Set up required urls for building buckets
    """
    fv_urls = []

    """
    Output - Where is data getting cached and archived?
    """

    """
    Pull Tickers from Screens
    """

    uniq_tickers = {
        'NFLX': True
    }
    tickers = []
    num_urls = len(fv_urls)

    log.info(
        '{} - pulling finviz tickers from urls={}'.format(
            label,
            num_urls))

    log.info(
        '{} - found finviz uniq_tickers={} from urls={}'.format(
            label,
            len(uniq_tickers),
            num_urls))

    for t in uniq_tickers:
        tickers.append(t)

    """
    Pull Ticker Data Feeds
    """

    run(tickers=tickers,
        fetch_mode=fetch_mode,
        iex_datasets=iex_datasets)

    """
    Determine Sell Conditions
    """

    """
    Determine Buy Conditions
    """

    """
    Send Alerts
    """

    log.info(
        '{} - done'.format(
            label))
# end of start


if __name__ == '__main__':
    start()
