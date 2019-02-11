"""
Get latest pricing from cached IEX pricing data
"""

import copy
import json
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.api_requests as api_requests
import analysis_engine.iex.consts as iex_consts
import analysis_engine.iex.extract_df_from_redis as iex_extract_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_pricing_on_date(
        ticker,
        date_str=None,
        label=None):
    """get_pricing_on_date

    Get the latest pricing data from the
    cached IEX data in redis. Use this to
    keep costs down!

    .. code-block:: python

        import analysis_engine.iex.get_pricing_on_date as iex_cache
        print(iex_cache.get_pricing_on_date('SPY'))
        print(iex_cache.get_pricing_on_date(
            ticker='SPY',
            date_str='2019-02-07'))

    :param ticker: ticker string
    :param date_str: optional - string date
        to pull data from redis. if ``None`` use
        today's date. format is
        ``ae_consts.COMMON_TICK_DATE_FORMAT``
    :param label: log label from tracking
    """

    ret_dict = {
        'status': ae_consts.NOT_SET,
        'pricing_type': None,
        'high': None,
        'low': None,
        'open': None,
        'close': None,
        'volume': None,
        'date': None,
        'minute': None,
        'average': None,
        'changeOverTime': None,
        'label': None,
        'marketAverage': None,
        'marketChangeOverTime': None,
        'marketClose': None,
        'marketHigh': None,
        'marketLow': None,
        'marketNotional': None,
        'marketNumberOfTrades': None,
        'marketOpen': None,
        'marketVolume': None,
        'notional': None,
        'numberOfTrades': None
    }

    use_date_str = None
    if date_str:
        use_date_str = (
            f'{ticker}_{date_str}')

    all_extract_reqs = api_requests.get_ds_dict(
        ticker=ticker,
        base_key=use_date_str,
        label=label)

    minute_key = all_extract_reqs['minute']
    daily_key = all_extract_reqs['daily']
    base_ex_req = {
        'ticker': ticker,
        's3_bucket': 'pricing',
        's3_key': minute_key,
        'redis_key': minute_key,
        's3_enabled': True,
        's3_access_key': ae_consts.S3_ACCESS_KEY,
        's3_secret_key': ae_consts.S3_SECRET_KEY,
        's3_region_name': ae_consts.S3_REGION_NAME,
        's3_address': ae_consts.S3_ADDRESS,
        's3_secure': ae_consts.S3_SECURE,
        'redis_address': ae_consts.REDIS_ADDRESS,
        'redis_password': ae_consts.REDIS_PASSWORD,
        'redis_db': ae_consts.REDIS_DB,
        'redis_expire': ae_consts.REDIS_EXPIRE,
        'redis_enabled': True,
        'fetch_mode': 'td',
        'analysis_type': None,
        'iex_datasets': [],
        'debug': False,
        'label': label,
        'celery_disabled': True
    }
    log.debug(
        f'{ticker} - minute={minute_key} daily={daily_key}')
    reqs = []
    minute_ex_req = copy.deepcopy(base_ex_req)
    minute_ex_req['ex_type'] = iex_consts.FETCH_MINUTE
    minute_ex_req['iex_datasets'] = [
        iex_consts.FETCH_MINUTE
    ]
    reqs.append(minute_ex_req)
    daily_ex_req = copy.deepcopy(base_ex_req)
    daily_ex_req['ex_type'] = iex_consts.FETCH_DAILY
    daily_ex_req['s3_key'] = daily_key
    daily_ex_req['redis_key'] = daily_key
    daily_ex_req['iex_datasets'] = [
        iex_consts.FETCH_DAILY
    ]
    reqs.append(daily_ex_req)
    try:
        for ex_req in reqs:
            iex_status = ae_consts.FAILED
            iex_df = None
            if ex_req['ex_type'] == iex_consts.FETCH_MINUTE:
                iex_status, iex_df = \
                    iex_extract_utils.extract_minute_dataset(
                        work_dict=ex_req)
            else:
                iex_status, iex_df = \
                    iex_extract_utils.extract_daily_dataset(
                        work_dict=ex_req)
            # end of extracting

            if ae_consts.is_df(df=iex_df):
                if 'date' in iex_df:
                    iex_df.sort_values(
                        by=[
                            'date'
                        ],
                        ascending=True)
                    ret_dict = json.loads(iex_df.iloc[-1].to_json())
                    if 'date' in ret_dict:
                        try:
                            ret_dict['date'] = ae_utils.epoch_to_dt(
                                epoch=int(ret_dict['date']/1000),
                                use_utc=False,
                                convert_to_est=False).strftime(
                                    ae_consts.COMMON_TICK_DATE_FORMAT)

                        except Exception as f:
                            log.critical(
                                f'failed converting {ret_dict} date to str '
                                f'with ex={f}')
                    if ex_req['ex_type'] == iex_consts.FETCH_MINUTE:
                        ret_dict['pricing_type'] = 'minute'
                        ret_dict['minute'] = ret_dict.get(
                            'date',
                            None)
                    else:
                        ret_dict['pricing_type'] = 'daily'
                    ret_dict['status'] = iex_status
                    return ret_dict
            # if a valid df then return it
    except Exception as e:
        log.critical(
            f'failed to get {ticker} iex minute data with ex={e}')
        ret_dict['status'] = ae_consts.ERR
    # end of try/ex to get latest pricing

    return ret_dict
# end of get_pricing_on_date
