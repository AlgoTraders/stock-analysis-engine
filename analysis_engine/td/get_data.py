"""
Parse data from TD

Supported environment variables:

::

    export DEBUG_TD_DATA=1

"""

import datetime
import copy
import analysis_engine.consts as ae_consts
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.td.fetch_data as td_fetch_data
import analysis_engine.td.consts as td_consts
import analysis_engine.work_tasks.publish_pricing_update as publisher
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_data_from_td(
        work_dict):
    """get_data_from_td

    Get pricing data from Tradier

    :param work_dict: request dictionary
    """
    label = 'get_data_from_td'

    log.debug(f'task - {label} - start work_dict={work_dict}')

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

        ticker = work_dict.get(
            'ticker',
            ae_consts.TICKER)
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

        td_req = None
        if ft_type == td_consts.FETCH_TD_CALLS or ft_str == 'tdcalls':
            ft_type == td_consts.FETCH_TD_CALLS
            td_req = api_requests.build_td_fetch_calls_request(
                label=label)
        elif ft_type == td_consts.FETCH_TD_PUTS or ft_str == 'tdputs':
            ft_type == td_consts.FETCH_TD_PUTS
            td_req = api_requests.build_td_fetch_puts_request(
                label=label)
        else:
            log.error(
                f'{label} - unsupported ft_type={ft_type} ft_str={ft_str} '
                f'ticker={ticker}')
            raise NotImplementedError
        # if supported fetch request type

        clone_keys = [
            'latest_pricing',
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
            if k in work_dict:
                td_req[k] = work_dict.get(
                    k,
                    f'{k}-missing-in-{label}')
        # end of cloning keys

        if not td_req:
            err = (
                f'{label} - ticker={td_req["ticker"]} did not build a TD '
                f'request for work={work_dict}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        else:
            log.debug(
                f'{label} - ticker={td_req["ticker"]} field={field} '
                f'orient={orient} fetch')
        # if invalid td request

        df = None
        try:
            if 'from' in work_dict:
                td_req['from'] = datetime.datetime.strptime(
                    '%Y-%m-%d %H:%M:%S',
                    work_dict['from'])
            status_df, df = td_fetch_data.fetch_data(
                work_dict=td_req,
                fetch_type=ft_type)

            if status_df == ae_consts.SUCCESS:
                rec['data'] = df.to_json(
                    orient=orient)
                rec['updated'] = datetime.datetime.utcnow().strftime(
                    '%Y-%m-%d %H:%M:%S')
            elif status_df == ae_consts.EMPTY:
                res = build_result.build_result(
                    status=ae_consts.ERR,
                    err=(
                        f'did not fetch any data'),
                    rec=rec)
                return res
            else:
                err = (
                    f'{label} - ticker={td_req["ticker"]} '
                    f'td_fetch_data.fetch_data field={ft_type} '
                    'failed fetch_data')
                log.critical(err)
                res = build_result.build_result(
                    status=ae_consts.ERR,
                    err=err,
                    rec=rec)
                return res
        except Exception as f:
            err = (
                f'{label} - ticker={td_req["ticker"]} field={ft_type} '
                f'failed fetch_data with ex={f}')
            log.critical(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        # end of try/ex

        if ae_consts.ev('DEBUG_TD_DATA', '0') == '1':
            log.debug(
                f'{label} ticker={td_req["ticker"]} field={field} '
                f'data={rec["data"]} to_json')
        else:
            log.debug(
                f'{label} ticker={td_req["ticker"]} field={field} to_json')
        # end of if/else found data

        upload_and_cache_req = copy.deepcopy(td_req)
        upload_and_cache_req['celery_disabled'] = True
        upload_and_cache_req['data'] = rec['data']
        if not upload_and_cache_req['data']:
            upload_and_cache_req['data'] = '{}'
        use_field = field
        if use_field == 'news':
            use_field = 'news1'
        if 'redis_key' in work_dict:
            upload_and_cache_req['redis_key'] = (
                f'''{work_dict.get(
                    'redis_key',
                    td_req['redis_key'])}_'''
                f'{use_field}')
        if 's3_key' in work_dict:
            upload_and_cache_req['s3_key'] = (
                f'''{work_dict.get(
                    's3_key',
                    td_req['s3_key'])}_'''
                f'{use_field}')

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
                f'{label} - failed to upload td data={upload_and_cache_req} '
                f'to s3_key={upload_and_cache_req["s3_key"]} and '
                f'redis_key={upload_and_cache_req["redis_key"]}')
            log.error(err)
        # end of try/ex to upload and cache

        if not rec['data']:
            log.debug(
                f'{label} - ticker={td_req["ticker"]} no Tradier data '
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
                'failed - get_data_from_td '
                f'dict={work_dict} with ex={e}'),
            rec=rec)
    # end of try/ex

    log.debug(
        'task - get_data_from_td done - '
        f'{label} - status={ae_consts.get_status(res["status"])} '
        f'err={res["err"]}')

    return res
# end of get_data_from_td
