"""
Common Fetch for any supported Get from IEX using HTTP

Supported environment variables:

::

    # debug the fetch routines with:
    export DEBUG_IEX_DATA=1

"""

import os
import datetime
import copy
import analysis_engine.consts as ae_consts
import analysis_engine.iex.consts as iex_consts
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.iex.fetch_data as iex_fetch_data
import analysis_engine.work_tasks.publish_pricing_update as publisher
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_data_from_iex(
        work_dict):
    """get_data_from_iex

    Get data from IEX - this requires an account

    :param work_dict: request dictionary
    """
    label = 'get_data_from_iex'

    log.debug(
        f'task - {label} - start '
        f'work_dict={work_dict}')

    rec = {
        'data': None,
        'updated': None
    }
    res = {
        'status': ae_consts.NOT_RUN,
        'err': None,
        'rec': rec
    }

    ticker = None
    field = None
    ft_type = None

    try:

        ticker = work_dict.get('ticker', ae_consts.TICKER)
        field = work_dict.get('field', 'daily')
        ft_type = work_dict.get('ft_type', None)
        ft_str = str(ft_type).lower()
        label = work_dict.get('label', label)
        orient = work_dict.get('orient', 'records')
        backfill_date = work_dict.get('backfill_date', None)
        verbose = work_dict.get('verbose', False)

        iex_req = None
        if ft_type == iex_consts.FETCH_DAILY or ft_str == 'daily':
            ft_type == iex_consts.FETCH_DAILY
            iex_req = api_requests.build_iex_fetch_daily_request(
                label=label)
        elif ft_type == iex_consts.FETCH_MINUTE or ft_str == 'minute':
            ft_type == iex_consts.FETCH_MINUTE
            iex_req = api_requests.build_iex_fetch_minute_request(
                label=label)
        elif ft_type == iex_consts.FETCH_QUOTE or ft_str == 'quote':
            ft_type == iex_consts.FETCH_QUOTE
            iex_req = api_requests.build_iex_fetch_quote_request(
                label=label)
        elif ft_type == iex_consts.FETCH_STATS or ft_str == 'stats':
            ft_type == iex_consts.FETCH_STATS
            iex_req = api_requests.build_iex_fetch_stats_request(
                label=label)
        elif ft_type == iex_consts.FETCH_PEERS or ft_str == 'peers':
            ft_type == iex_consts.FETCH_PEERS
            iex_req = api_requests.build_iex_fetch_peers_request(
                label=label)
        elif ft_type == iex_consts.FETCH_NEWS or ft_str == 'news':
            ft_type == iex_consts.FETCH_NEWS
            iex_req = api_requests.build_iex_fetch_news_request(
                label=label)
        elif ft_type == iex_consts.FETCH_FINANCIALS or ft_str == 'financials':
            ft_type == iex_consts.FETCH_FINANCIALS
            iex_req = api_requests.build_iex_fetch_financials_request(
                label=label)
        elif ft_type == iex_consts.FETCH_EARNINGS or ft_str == 'earnings':
            ft_type == iex_consts.FETCH_EARNINGS
            iex_req = api_requests.build_iex_fetch_earnings_request(
                label=label)
        elif ft_type == iex_consts.FETCH_DIVIDENDS or ft_str == 'dividends':
            ft_type == iex_consts.FETCH_DIVIDENDS
            iex_req = api_requests.build_iex_fetch_dividends_request(
                label=label)
        elif ft_type == iex_consts.FETCH_COMPANY or ft_str == 'company':
            ft_type == iex_consts.FETCH_COMPANY
            iex_req = api_requests.build_iex_fetch_company_request(
                label=label)
        else:
            log.error(
                f'{label} - unsupported ft_type={ft_type} '
                f'ft_str={ft_str} ticker={ticker}')
            raise NotImplementedError
        # if supported fetch request type

        iex_req['ticker'] = ticker
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
            if k in iex_req:
                iex_req[k] = work_dict.get(k, f'{k}-missing-in-{label}')
        # end of cloning keys

        if not iex_req:
            err = (
                f'{label} - ticker={ticker} '
                f'did not build an IEX request '
                f'for work={work_dict}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        else:
            log.debug(
                f'{label} - ticker={ticker} '
                f'field={field} '
                f'orient={orient} fetch')
        # if invalid iex request

        df = None
        try:
            if 'from' in work_dict:
                iex_req['from'] = datetime.datetime.strptime(
                    '%Y-%m-%d %H:%M:%S',
                    work_dict['from'])
            if backfill_date:
                iex_req['backfill_date'] = backfill_date
                iex_req['redis_key'] = (
                    f'{ticker}_{backfill_date}_{field}')
                iex_req['s3_key'] = (
                    f'{ticker}_{backfill_date}_{field}')

            if os.getenv('SHOW_SUCCESS', '0') == '1':
                log.info(
                    f'fetching IEX {field} req={iex_req}')
            else:
                log.debug(
                    f'fetching IEX {field} req={iex_req}')

            df = iex_fetch_data.fetch_data(
                work_dict=iex_req,
                fetch_type=ft_type,
                verbose=verbose)
            rec['data'] = df.to_json(
                orient=orient,
                date_format='iso')
            rec['updated'] = datetime.datetime.utcnow().strftime(
                '%Y-%m-%d %H:%M:%S')
        except Exception as f:
            log.error(
                f'{label} - ticker={ticker} field={ft_type} '
                f'failed fetch_data '
                f'with ex={f}')
        # end of try/ex

        if ae_consts.ev('DEBUG_IEX_DATA', '0') == '1':
            log.debug(
                f'{label} ticker={ticker} '
                f'field={field} data={rec["data"]} to_json')
        else:
            log.debug(
                f'{label} ticker={ticker} field={field} to_json')
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
            rk = work_dict.get('redis_key', iex_req['redis_key'])
            if backfill_date:
                rk = f'{ticker}_{backfill_date}'
            upload_and_cache_req['redis_key'] = (
                f'{rk}_{use_field}')
        if 's3_key' in work_dict:
            sk = work_dict.get('s3_key', iex_req['s3_key'])
            if backfill_date:
                sk = f'{ticker}_{backfill_date}'
            upload_and_cache_req['s3_key'] = (
                f'{sk}_{use_field}')

        try:
            update_res = publisher.run_publish_pricing_update(
                work_dict=upload_and_cache_req)
            update_status = update_res.get(
                'status',
                ae_consts.NOT_SET)
            log.debug(
                f'{label} publish update '
                f'status={ae_consts.get_status(status=update_status)} '
                f'data={update_res}')
        except Exception:
            err = (
                f'{label} - failed to upload iex '
                f'data={upload_and_cache_req} to '
                f'to s3_key={upload_and_cache_req["s3_key"]} '
                f'and redis_key={upload_and_cache_req["redis_key"]}')
            log.error(err)
        # end of try/ex to upload and cache

        if not rec['data']:
            log.debug(
                f'{label} - ticker={ticker} no IEX data '
                f'field={field} to publish')
        # end of if/else

        res = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=(
                f'failed - get_data_from_iex '
                f'dict={work_dict} with ex={e}'),
            rec=rec)
    # end of try/ex

    log.debug(
        f'task - get_data_from_iex done - '
        f'{label} - '
        f'status={ae_consts.get_status(res["status"])} '
        f'err={res["err"]}')

    return res
# end of get_data_from_iex
