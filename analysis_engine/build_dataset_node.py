"""
Build a dictionary by extracting all required pricing datasets
for the algorithm's indicators out of Redis

This dictionary should be passed to an algorithm's ``handle_data``
method like:

.. code-block:: python

    algo.handle_data(build_dataset_node())
"""

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.api_requests as api_requests
import analysis_engine.iex.extract_df_from_redis as iex_extract_utils
import analysis_engine.td.extract_df_from_redis as td_extract_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_dataset_node(
        ticker,
        datasets,
        date=None,
        service_dict=None,
        log_label=None,
        redis_enabled=True,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        redis_key=None,
        s3_enabled=True,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=False,
        s3_key=None,
        verbose=False):
    """build_dataset_node

    Helper for building a dictionary that of
    cached datasets from redis.

    The datasets should be built from
    off the algorithm's config indicators
    ``uses_data`` fields which if not
    set will default to ``minute`` data

    :param ticker: string ticker
    :param datasets: list of string dataset names
        to extract from redis
    :param date: optional - string datetime formatted
        ``YYYY-MM-DD``
        (default is last trading close date)
    :param service_dict: optional - dictionary for all
        service connectivity to Redis and Minio if not
        set the arguments for all ``s3_*`` and ``redis_*``
        will be used to lookup data in Redis and Minio

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``True``)
    :param redis_address: Redis connection string
        format is ``host:port``
        (default is ``localhost:6379``)
    :param redis_db: Redis db to use
        (default is ``0``)
    :param redis_password: optional - Redis password
        (default is ``None``)
    :param redis_expire: optional - Redis expire value
        (default is ``None``)
    :param redis_key: optional - redis key not used
        (default is ``None``)

    :param s3_enabled: bool - toggle for turning on/off
        Minio or AWS S3
        (default is ``True``)
    :param s3_address: Minio S3 connection string address
        format is ``host:port``
        (default is ``localhost:9000``)
    :param s3_bucket: S3 Bucket for storing the artifacts
        (default is ``dev``) which should be viewable on a browser:
        http://localhost:9000/minio/dev/
    :param s3_access_key: S3 Access key
        (default is ``trexaccesskey``)
    :param s3_secret_key: S3 Secret key
        (default is ``trex123321``)
    :param s3_region_name: S3 region name
        (default is ``us-east-1``)
    :param s3_secure: Transmit using tls encryption
        (default is ``False``)
    :param s3_key: optional s3 key not used
        (default is ``None``)

    **Debugging**

    :param log_label: optional - log label string
    :param verbose: optional - flag for debugging
        (default to ``False``)
    """

    label = log_label
    if not label:
        label = 'build_bt'

    if not date:
        date = ae_utils.get_last_close_str()

    td_convert_to_datetime = (
        ae_consts.TRADIER_CONVERT_TO_DATETIME)

    date_key = f'{ticker}_{date}'

    base_req = api_requests.get_ds_dict(
        ticker=ticker,
        base_key=date_key,
        ds_id=label,
        service_dict=service_dict)

    if not service_dict:
        base_req['redis_enabled'] = redis_enabled
        base_req['redis_address'] = (
            redis_address if redis_address else ae_consts.REDIS_ADDRESS)
        base_req['redis_password'] = (
            redis_password if redis_password else ae_consts.REDIS_PASSWORD)
        base_req['redis_db'] = (
            redis_db if redis_db else ae_consts.REDIS_DB)
        base_req['redis_expire'] = (
            redis_expire if redis_expire else ae_consts.REDIS_EXPIRE)
        base_req['s3_enabled'] = s3_enabled
        base_req['s3_bucket'] = (
            s3_bucket if s3_bucket else ae_consts.S3_BUCKET)
        base_req['s3_address'] = (
            s3_address if s3_address else ae_consts.S3_ADDRESS)
        base_req['s3_secure'] = (
            s3_secure if s3_secure else ae_consts.S3_SECURE)
        base_req['s3_region_name'] = (
            s3_region_name if s3_region_name else ae_consts.S3_REGION_NAME)
        base_req['s3_access_key'] = (
            s3_access_key if s3_access_key else ae_consts.S3_ACCESS_KEY)
        base_req['s3_secret_key'] = (
            s3_secret_key if s3_secret_key else ae_consts.S3_SECRET_KEY)
        base_req['redis_key'] = date_key
        base_req['s3_key'] = date_key

    if verbose:
        log.info(
            f'extracting {date_key} req: {base_req}')
        """
        for showing connectivity args in the logs
        log.debug(
            f'bt {date_key} {ae_consts.ppj(base_req)}')
        """

    iex_daily_status = ae_consts.FAILED
    iex_minute_status = ae_consts.FAILED
    iex_quote_status = ae_consts.FAILED
    iex_stats_status = ae_consts.FAILED
    iex_peers_status = ae_consts.FAILED
    iex_news_status = ae_consts.FAILED
    iex_financials_status = ae_consts.FAILED
    iex_earnings_status = ae_consts.FAILED
    iex_dividends_status = ae_consts.FAILED
    iex_company_status = ae_consts.FAILED
    td_calls_status = ae_consts.FAILED
    td_puts_status = ae_consts.FAILED

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
    td_calls_df = None
    td_puts_df = None

    if 'daily' in datasets:
        iex_daily_status, iex_daily_df = \
            iex_extract_utils.extract_daily_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_daily_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_daily={ticker}')
    if 'minute' in datasets:
        iex_minute_status, iex_minute_df = \
            iex_extract_utils.extract_minute_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_minute_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_minute={ticker}')
    if 'quote' in datasets:
        iex_quote_status, iex_quote_df = \
            iex_extract_utils.extract_quote_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_quote_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_quote={ticker}')
    if 'stats' in datasets:
        iex_stats_df, iex_stats_df = \
            iex_extract_utils.extract_stats_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_stats_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_stats={ticker}')
    if 'peers' in datasets:
        iex_peers_df, iex_peers_df = \
            iex_extract_utils.extract_peers_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_peers_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_peers={ticker}')
    if 'news' in datasets:
        iex_news_status, iex_news_df = \
            iex_extract_utils.extract_news_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_news_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_news={ticker}')
    if 'financials' in datasets:
        iex_financials_status, iex_financials_df = \
            iex_extract_utils.extract_financials_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_financials_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_financials={ticker}')
    if 'earnings' in datasets:
        iex_earnings_status, iex_earnings_df = \
            iex_extract_utils.extract_earnings_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_earnings_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_earnings={ticker}')
    if 'dividends' in datasets:
        iex_dividends_status, iex_dividends_df = \
            iex_extract_utils.extract_dividends_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_dividends_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_dividends={ticker}')
    if 'company' in datasets:
        iex_company_status, iex_company_df = \
            iex_extract_utils.extract_company_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if iex_company_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract iex_company={ticker}')
    # end of iex extracts

    """
    Yahoo disabled on Jan 2019

    yahoo_news_status = ae_consts.FAILED
    yahoo_options_status = ae_consts.FAILED
    yahoo_pricing_status = ae_consts.FAILED
    yahoo_option_calls_df = None
    yahoo_option_puts_df = None
    yahoo_pricing_df = None
    yahoo_news_df = None

    if 'options' in datasets:
        yahoo_options_status, yahoo_option_calls_df = \
            yahoo_extract_utils.extract_option_calls_dataset(
                base_req)
        yahoo_options_status, yahoo_option_puts_df = \
            yahoo_extract_utils.extract_option_puts_dataset(
                base_req)
        if yahoo_options_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract yahoo_options={ticker}')
    if 'pricing' in datasets:
        yahoo_pricing_status, yahoo_pricing_df = \
            yahoo_extract_utils.extract_pricing_dataset(
                base_req)
        if yahoo_pricing_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract yahoo_pricing={ticker}')
    if 'news' in datasets:
        yahoo_news_status, yahoo_news_df = \
            yahoo_extract_utils.extract_yahoo_news_dataset(
                base_req)
        if yahoo_news_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract yahoo_news={ticker}')
    # end of yahoo extracts
    """

    """
    Tradier Extraction
    Debug by setting:

    base_req['verbose_td'] = True
    """
    if (
            'calls' in datasets or
            'tdcalls' in datasets):
        td_calls_status, td_calls_df = \
            td_extract_utils.extract_option_calls_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if td_calls_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract tdcalls={ticker}')
        else:
            if ae_consts.is_df(
                    df=td_calls_df):
                for c in td_convert_to_datetime:
                    if c in td_calls_df:
                        td_calls_df[c] = pd.to_datetime(
                            td_calls_df[c],
                            format=ae_consts.COMMON_TICK_DATE_FORMAT)
                if 'date' in td_calls_df:
                    td_calls_df.sort_values(
                        'date',
                        ascending=True)
        # end of converting dates
    # end of Tradier calls extraction

    if (
            'puts' in datasets or
            'tdputs' in datasets):
        td_puts_status, td_puts_df = \
            td_extract_utils.extract_option_puts_dataset(
                ticker=ticker,
                date=date,
                work_dict=base_req,
                verbose=verbose)
        if td_puts_status != ae_consts.SUCCESS:
            if verbose:
                log.warn(f'unable to extract tdputs={ticker}')
        else:
            if ae_consts.is_df(
                    df=td_puts_df):
                for c in td_convert_to_datetime:
                    if c in td_puts_df:
                        td_puts_df[c] = pd.to_datetime(
                            td_puts_df[c],
                            format=ae_consts.COMMON_TICK_DATE_FORMAT)
                if 'date' in td_puts_df:
                    td_puts_df.sort_values(
                        'date',
                        ascending=True)
        # end of converting dates
    # end of Tradier puts extraction

    ticker_data = {
        'daily': iex_daily_df,
        'minute': iex_minute_df,
        'quote': iex_quote_df,
        'stats': iex_stats_df,
        'peers': iex_peers_df,
        'news1': iex_news_df,
        'financials': iex_financials_df,
        'earnings': iex_earnings_df,
        'dividends': iex_dividends_df,
        'company': iex_company_df,
        'tdcalls': td_calls_df,
        'tdputs': td_puts_df,
        'calls': None,  # yahoo - here for legacy
        'news': None,  # yahoo - here for legacy
        'pricing': None,  # yahoo - here for legacy
        'puts': None  # yahoo - here for legacy
    }

    return ticker_data
# end of build_dataset_node
