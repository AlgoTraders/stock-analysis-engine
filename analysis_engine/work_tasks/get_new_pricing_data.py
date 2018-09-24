"""
Get New Pricing Data
"""

import datetime
import analysis_engine.build_result as build_result
import analysis_engine.get_task_results
import analysis_engine.work_tasks.custom_task
import analysis_engine.options_dates
import analysis_engine.get_pricing
import analysis_engine.work_tasks.publish_pricing_update as \
    publisher
import pinance
from celery.task import task
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import TICKER
from analysis_engine.consts import TICKER_ID
from analysis_engine.consts import ENABLED_S3_UPLOAD
from analysis_engine.consts import S3_ACCESS_KEY
from analysis_engine.consts import S3_SECRET_KEY
from analysis_engine.consts import S3_REGION_NAME
from analysis_engine.consts import S3_ADDRESS
from analysis_engine.consts import S3_SECURE
from analysis_engine.consts import S3_BUCKET
from analysis_engine.consts import S3_KEY
from analysis_engine.consts import ENABLED_REDIS_PUBLISH
from analysis_engine.consts import REDIS_ADDRESS
from analysis_engine.consts import REDIS_KEY
from analysis_engine.consts import REDIS_PASSWORD
from analysis_engine.consts import REDIS_DB
from analysis_engine.consts import REDIS_EXPIRE
from analysis_engine.consts import get_status
from analysis_engine.consts import ev
from analysis_engine.consts import ppj
from analysis_engine.consts import is_celery_disabled


log = build_colorized_logger(
    name=__name__)


@task(
    bind=True,
    base=analysis_engine.work_tasks.custom_task.CustomTask,
    queue='get_new_pricing_data')
def get_new_pricing_data(
        self,
        work_dict):
    """get_new_pricing_data

    Get Ticker information on:

    - prices - turn off with ``work_dict.get_pricing = False``
    - news - turn off with ``work_dict.get_news = False``
    - options - turn off with ``work_dict.get_options = False``

    :param work_dict: dictionary for key/values
    """

    label = 'get_new_pricing_data'

    log.info((
        'task - {} - start '
        'work_dict={}').format(
            label,
            work_dict))

    ticker = TICKER
    ticker_id = TICKER_ID
    rec = {
        'pricing': None,
        'options': None,
        'news': None,
        'exp_date': None,
        'date': None,
        'updated': None
    }
    res = {
        'status': NOT_RUN,
        'err': None,
        'rec': rec
    }

    try:
        ticker = work_dict.get(
            'ticker',
            TICKER)
        ticker_id = work_dict.get(
            'ticker_id',
            TICKER_ID)
        s3_bucket = work_dict.get(
            's3_bucket',
            S3_BUCKET)
        s3_key = work_dict.get(
            's3_key',
            S3_KEY)
        redis_key = work_dict.get(
            'redis_key',
            REDIS_KEY)
        exp_date = work_dict.get(
            'exp_date',
            None)
        cur_date = datetime.datetime.utcnow()
        cur_close = None
        cur_strike = work_dict.get(
            'strike',
            None)
        contract_type = str(work_dict.get(
            'contract',
            'C')).upper()
        get_pricing = work_dict.get(
            'get_pricing',
            True)
        get_news = work_dict.get(
            'get_news',
            True)
        get_options = work_dict.get(
            'get_options',
            True)
        label = work_dict.get(
            'label',
            label)
        num_news_rec = 0
        num_options_chains = 0
        cur_high = -1
        cur_low = -1
        cur_open = -1
        cur_close = -1
        cur_volume = -1

        if not exp_date:
            exp_date = analysis_engine.options_dates.option_expiration(
                date=exp_date)
        else:
            exp_date = datetime.datetime.strptime(
                exp_date,
                '%Y-%m-%d')

        rec['updated'] = cur_date.strftime('%Y-%m-%d %H:%M:%S')
        log.info((
            '{} getting pricing for ticker={} '
            'cur_date={} exp_date={}').format(
                label,
                ticker,
                cur_date,
                exp_date))

        ticker_results = pinance.Pinance(ticker)

        if get_pricing:
            log.info((
                '{} getting ticker={} pricing').format(
                    label,
                    ticker))
            ticker_results.get_quotes()
            if ticker_results.quotes_data:
                rec['pricing'] = ticker_results.quotes_data

                cur_high = rec['pricing'].get(
                    'regularMarketDayHigh',
                    None)
                cur_low = rec['pricing'].get(
                    'regularMarketDayLow',
                    None)
                cur_open = rec['pricing'].get(
                    'regularMarketOpen',
                    None)
                cur_close = rec['pricing'].get(
                    'regularMarketPreviousClose',
                    None)
                cur_volume = rec['pricing'].get(
                    'regularMarketVolume',
                    None)
                rec['pricing']['high'] = cur_high
                rec['pricing']['low'] = cur_low
                rec['pricing']['open'] = cur_open
                rec['pricing']['close'] = cur_close
                rec['pricing']['volume'] = cur_volume
            else:
                log.error((
                    '{} ticker={} missing quotes_data').format(
                        label,
                        ticker))
            # end of if ticker_results.quotes_data

            log.info((
                '{} ticker={} close={} vol={}').format(
                    label,
                    ticker,
                    cur_close,
                    cur_volume))
        else:
            log.info((
                '{} skip - getting ticker={} pricing').format(
                    label,
                    ticker,
                    get_pricing))
        # if get_pricing

        if get_news:
            log.info((
                '{} getting ticker={} news').format(
                    label,
                    ticker))
            ticker_results.get_news()
            if ticker_results.news_data:
                rec['news'] = ticker_results.news_data
            # end of if ticker_results.news_data
        else:
            log.info((
                '{} skip - getting ticker={} news').format(
                    label,
                    ticker))
        # end if get_news

        if get_options:
            use_date = exp_date.strftime('%Y-%m-%d')
            if cur_close:
                cur_strike = int(cur_close)
            if not cur_strike:
                cur_strike = 287

            num_news_rec = 0
            if rec['news']:
                num_news_rec = len(rec['news'])
            log.info((
                '{} ticker={} num_news={} get options close={} '
                'exp_date={} contract={} strike={}').format(
                    label,
                    ticker,
                    num_news_rec,
                    cur_close,
                    use_date,
                    contract_type,
                    cur_strike))

            rec['options'] = \
                analysis_engine.get_pricing.get_options(
                    ticker=ticker,
                    exp_date_str=use_date,
                    contract_type=contract_type,
                    strike=cur_strike)

            num_options_chains = len(rec['options'])
        else:
            log.info((
                '{} skip - getting ticker={} options').format(
                    label,
                    ticker))
        # end of if get_options

        update_req = {
            'data': {
                'pricing': rec.get('pricing', None),
                'news': rec.get('news', None),
                'options': rec.get('options', None)
            }
        }
        update_req['ticker'] = ticker
        update_req['ticker_id'] = ticker_id
        update_req['strike'] = cur_strike
        update_req['contract'] = contract_type
        update_req['s3_enabled'] = work_dict.get(
            's3_enabled',
            ENABLED_S3_UPLOAD)
        update_req['redis_enabled'] = work_dict.get(
            'redis_enabled',
            ENABLED_REDIS_PUBLISH)
        update_req['s3_bucket'] = s3_bucket
        update_req['s3_key'] = s3_key
        update_req['s3_access_key'] = work_dict.get(
            's3_access_key',
            S3_ACCESS_KEY)
        update_req['s3_secret_key'] = work_dict.get(
            's3_secret_key',
            S3_SECRET_KEY)
        update_req['s3_region_name'] = work_dict.get(
            's3_region_name',
            S3_REGION_NAME)
        update_req['s3_address'] = work_dict.get(
            's3_address',
            S3_ADDRESS)
        update_req['s3_secure'] = work_dict.get(
            's3_secure',
            S3_SECURE)
        update_req['redis_key'] = redis_key
        update_req['redis_address'] = work_dict.get(
            'redis_address',
            REDIS_ADDRESS)
        update_req['redis_password'] = work_dict.get(
            'redis_password',
            REDIS_PASSWORD)
        update_req['redis_db'] = work_dict.get(
            'redis_db',
            REDIS_DB)
        update_req['redis_expire'] = work_dict.get(
            'redis_expire',
            REDIS_EXPIRE)
        update_req['updated'] = rec['updated']
        update_req['label'] = label
        update_req['celery_disabled'] = True

        if ev('DEBUG_GET_PRICING', '0') == '1':
            log.info((
                '{} updating pricing for ticker={} close={} '
                'options={} news={} data={}').format(
                    label,
                    ticker,
                    cur_close,
                    num_options_chains,
                    num_news_rec,
                    ppj(update_req)))

        else:
            log.info((
                '{} updating pricing for ticker={} close={} '
                'options={} news={}').format(
                    label,
                    ticker,
                    cur_close,
                    num_options_chains,
                    num_news_rec))

        update_res = publisher.run_publish_pricing_update(
            work_dict=update_req)

        log.info((
            '{} ticker={} update_res status={} data={}'.format(
                label,
                ticker,
                get_status(update_res['status']),
                update_res)))

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - get_new_pricing_data '
                'dict={} with ex={}').format(
                    work_dict,
                    e))
        log.error((
            '{} - {}').format(
                label,
                res['err']))
    # end of try/ex

    log.info((
        'task - {} - done - status={}').format(
            label,
            get_status(res['status'])))

    # if celery is disabled make sure to return the results
    if is_celery_disabled(work_dict=work_dict):
        return res
    else:
        return analysis_engine.get_task_results.get_task_results(
            result=res)
# end of get_new_pricing_data


def run_get_new_pricing_data(
        work_dict):
    """run_get_new_pricing_data

    Celery wrapper for running without celery

    :param work_dict: task data
    """

    label = work_dict.get(
        'label',
        '')

    log.info(
        'run_get_new_pricing_data - {} - start'.format(
            label))

    response = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    # allow running without celery
    if is_celery_disabled():
        work_dict['celery_disabled'] = True
        response = get_new_pricing_data(
            work_dict)
    else:
        task_res = get_new_pricing_data.delay(
            work_dict=work_dict)
        rec = {
            'task_id': task_res
        }
        response = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)
    # if celery enabled

    log.info(
        'run_get_new_pricing_data - {} - done '
        'status={} err={} rec={}'.format(
            label,
            get_status(response['status']),
            response['err'],
            response['rec']))

    return response
# end of run_get_new_pricing_data
