"""
Parse data from IEX

Supported environment variables:

::

    export DEBUG_IEX_DATA=1

"""

import datetime
import copy
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.iex.fetch_data as iex_fetch_data
import analysis_engine.work_tasks.publish_pricing_update as \
    publisher
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import NOT_SET
from analysis_engine.consts import get_status
from analysis_engine.consts import ev
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

log = build_colorized_logger(
    name=__name__)


def get_data_from_iex(
        work_dict):
    """get_data_from_iex

    Get pricing from iex

    :param work_dict: request dictionary
    """
    label = 'get_data_from_iex'

    log.info(
        'task - {} - start '
        'work_dict={}'.format(
            label,
            work_dict))

    rec = {
        'data': None,
        'updated': None
    }
    res = {
        'status': NOT_RUN,
        'err': None,
        'rec': rec
    }

    ticker = None
    field = None
    ft_type = None

    try:

        ticker = work_dict.get(
            'ticker',
            TICKER)
        field = work_dict.get(
            'field',
            'daily')
        ft_type = work_dict.get(
            'ft_type',
            None)
        ft_str = str(ft_type).lower()
        label = work_dict.get(
            'label',
            label)
        orient = work_dict.get(
            'orient',
            'records')

        iex_req = None
        if ft_type == FETCH_DAILY or ft_str == 'daily':
            ft_type == FETCH_DAILY
            iex_req = api_requests.build_iex_fetch_daily_request(
                label=label)
        elif ft_type == FETCH_MINUTE or ft_str == 'minute':
            ft_type == FETCH_MINUTE
            iex_req = api_requests.build_iex_fetch_minute_request(
                label=label)
        elif ft_type == FETCH_QUOTE or ft_str == 'quote':
            ft_type == FETCH_QUOTE
            iex_req = api_requests.build_iex_fetch_quote_request(
                label=label)
        elif ft_type == FETCH_STATS or ft_str == 'stats':
            ft_type == FETCH_STATS
            iex_req = api_requests.build_iex_fetch_stats_request(
                label=label)
        elif ft_type == FETCH_PEERS or ft_str == 'peers':
            ft_type == FETCH_PEERS
            iex_req = api_requests.build_iex_fetch_peers_request(
                label=label)
        elif ft_type == FETCH_NEWS or ft_str == 'news':
            ft_type == FETCH_NEWS
            iex_req = api_requests.build_iex_fetch_news_request(
                label=label)
        elif ft_type == FETCH_FINANCIALS or ft_str == 'financials':
            ft_type == FETCH_FINANCIALS
            iex_req = api_requests.build_iex_fetch_financials_request(
                label=label)
        elif ft_type == FETCH_EARNINGS or ft_str == 'earnings':
            ft_type == FETCH_EARNINGS
            iex_req = api_requests.build_iex_fetch_earnings_request(
                label=label)
        elif ft_type == FETCH_DIVIDENDS or ft_str == 'dividends':
            ft_type == FETCH_DIVIDENDS
            iex_req = api_requests.build_iex_fetch_dividends_request(
                label=label)
        elif ft_type == FETCH_COMPANY or ft_str == 'company':
            ft_type == FETCH_COMPANY
            iex_req = api_requests.build_iex_fetch_company_request(
                label=label)
        else:
            log.error(
                '{} - unsupported ft_type={} ft_str={} ticker={}'.format(
                    label,
                    ft_type,
                    ft_str,
                    ticker))
            raise NotImplemented
        # if supported fetch request type

        clone_keys = [
            'ticker',
            's3_address',
            's3_bucket',
            's3_key',
            'redis_address',
            'redis_db',
            'redis_password',
            'redis_key'
        ]

        for k in clone_keys:
            iex_req[k] = work_dict.get(
                k,
                '{}-missing-in-{}'.format(
                    k,
                    label))
        # end of cloning keys

        if not iex_req:
            err = (
                '{} - ticker={} did not build an IEX request '
                'for work={}'.format(
                    label,
                    iex_req['ticker'],
                    work_dict))
            log.error(err)
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)
            return res
        else:
            log.info(
                '{} - ticker={} field={} '
                'orient={} fetch'.format(
                    label,
                    iex_req['ticker'],
                    field,
                    orient))
        # if invalid iex request

        df = None
        try:
            if 'from' in work_dict:
                iex_req['from'] = datetime.datetime.strptime(
                    '%Y-%m-%d %H:%M:%S',
                    work_dict['from'])
            df = iex_fetch_data.fetch_data(
                work_dict=iex_req,
                fetch_type=ft_type)
            rec['data'] = df.to_json(
                orient=orient,
                date_format='iso')
            rec['updated'] = datetime.datetime.utcnow().strftime(
                '%Y-%m-%d %H:%M:%S')
        except Exception as f:
            log.error(
                '{} - ticker={} field={} failed fetch_data '
                'with ex={}'.format(
                    label,
                    iex_req['ticker'],
                    ft_type,
                    f))
        # end of try/ex

        if ev('DEBUG_IEX_DATA', '0') == '1':
            log.info(
                '{} ticker={} field={} data={} to_json'.format(
                    label,
                    iex_req['ticker'],
                    field,
                    rec['data']))
        else:
            log.info(
                '{} ticker={} field={} to_json'.format(
                    label,
                    iex_req['ticker'],
                    field))
        # end of if/else found data

        upload_and_cache_req = copy.deepcopy(iex_req)
        upload_and_cache_req['celery_disabled'] = True
        upload_and_cache_req['data'] = rec['data']
        if not upload_and_cache_req['data']:
            upload_and_cache_req['data'] = '{}'
        use_field = field
        if use_field == 'news':
            use_field = 'news1'
        if 'redis_key' in work_dict:
            upload_and_cache_req['redis_key'] = '{}_{}'.format(
                work_dict.get(
                    'redis_key',
                    iex_req['redis_key']),
                use_field)
        if 's3_key' in work_dict:
            upload_and_cache_req['s3_key'] = '{}_{}'.format(
                work_dict.get(
                    's3_key',
                    iex_req['s3_key']),
                use_field)

        try:
            update_res = publisher.run_publish_pricing_update(
                work_dict=upload_and_cache_req)
            update_status = update_res.get(
                'status',
                NOT_SET)
            log.info(
                '{} publish update status={} data={}'.format(
                    label,
                    get_status(status=update_status),
                    update_res))
        except Exception as f:
            err = (
                '{} - failed to upload iex data={} to '
                'to s3_key={} and redis_key={}'.format(
                    label,
                    upload_and_cache_req,
                    upload_and_cache_req['s3_key'],
                    upload_and_cache_req['redis_key']))
            log.error(err)
        # end of try/ex to upload and cache

        if not rec['data']:
            log.info(
                '{} - ticker={} no IEX data field={} to publish'.format(
                    label,
                    iex_req['ticker'],
                    field))
        # end of if/else

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - get_data_from_iex '
                'dict={} with ex={}').format(
                    work_dict,
                    e),
            rec=rec)
    # end of try/ex

    log.info(
        'task - get_data_from_iex done - '
        '{} - status={} err={}'.format(
            label,
            get_status(res['status']),
            res['err']))

    return res
# end of get_data_from_iex
