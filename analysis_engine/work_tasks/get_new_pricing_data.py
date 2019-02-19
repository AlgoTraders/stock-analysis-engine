"""
**Get New Pricing Data Task**

This will fetch data (pricing, financials, earnings, dividends, options,
and more) from these sources:

#.  IEX

#.  Tradier

#.  Yahoo - disabled as of 2019/01/03

**Detailed example for getting new pricing data**

.. code-block:: python

    import datetime
    import build_get_new_pricing_request
    from analysis_engine.api_requests
    from analysis_engine.work_tasks.get_new_pricing_data
        import get_new_pricing_data

    # store data
    cur_date = datetime.datetime.now().strftime('%Y-%m-%d')
    work = build_get_new_pricing_request(
        label=f'get-pricing-{cur_date}')
    work['ticker'] = 'TSLA'
    work['s3_bucket'] = 'pricing'
    work['s3_key'] = f'{work["ticker"]}-{cur_date}'
    work['redis_key'] = f'{work["ticker"]}-{cur_date}'
    work['celery_disabled'] = True
    res = get_new_pricing_data(
        work)
    print('full result dictionary:')
    print(res)
    if res['data']:
        print(
            'named datasets returned as '
            'json-serialized pandas DataFrames:')
        for k in res['data']:
            print(f' - {k}')

.. warning:: When fetching pricing data from sources like IEX,
    Please ensure the returned values are
    not serialized pandas Dataframes to prevent
    issues with celery task results. Instead
    it is preferred to returned a ``df.to_json()``
    before sending the results into the
    results backend.

.. tip:: This task uses the `analysis_engine.work_tasks.
    custom_task.CustomTask class <https://github.com/A
    lgoTraders/stock-analysis-engine/blob/master/anal
    ysis_engine/work_tasks/custom_task.py>`__ for
    task event handling.

**Sample work_dict request for this method**

`analysis_engine.api_requests.build_get_new_pricing_request <https://
github.com/AlgoTraders/stock-analysis-engine/blob/master/
analysis_engine/api_requests.py#L49>`__

**Supported Environment Variables**

::

    export DEBUG_RESULTS=1

"""

import datetime
import copy
import celery
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.iex.consts as iex_consts
import analysis_engine.iex.get_pricing_on_date as iex_pricing
import analysis_engine.td.consts as td_consts
import analysis_engine.build_result as build_result
import analysis_engine.get_task_results as get_task_results
import analysis_engine.work_tasks.custom_task as custom_task
import analysis_engine.options_dates as opt_dates
import analysis_engine.work_tasks.publish_pricing_update as publisher
import analysis_engine.yahoo.get_data as yahoo_data
import analysis_engine.iex.get_data as iex_data
import analysis_engine.td.get_data as td_data
import analysis_engine.send_to_slack as slack_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


@celery.task(
    bind=True,
    base=custom_task.CustomTask,
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

    log.debug(
        f'task - {label} - start '
        f'work_dict={work_dict}')

    num_success = 0
    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    rec = {
        'pricing': None,
        'options': None,
        'calls': None,
        'puts': None,
        'news': None,
        'daily': None,
        'minute': None,
        'quote': None,
        'stats': None,
        'peers': None,
        'iex_news': None,
        'financials': None,
        'earnings': None,
        'dividends': None,
        'company': None,
        'exp_date': None,
        'publish_pricing_update': None,
        'num_success': num_success,
        'date': ae_utils.utc_now_str(),
        'updated': None,
        'version': ae_consts.DATASET_COLLECTION_VERSION
    }
    res = {
        'status': ae_consts.NOT_RUN,
        'err': None,
        'rec': rec
    }

    try:
        ticker = work_dict.get(
            'ticker',
            ticker)
        ticker_id = work_dict.get(
            'ticker_id',
            ae_consts.TICKER_ID)
        s3_bucket = work_dict.get(
            's3_bucket',
            ae_consts.S3_BUCKET)
        s3_key = work_dict.get(
            's3_key',
            ae_consts.S3_KEY)
        redis_key = work_dict.get(
            'redis_key',
            ae_consts.REDIS_KEY)
        exp_date = work_dict.get(
            'exp_date',
            None)
        cur_date = ae_utils.last_close()
        cur_strike = work_dict.get(
            'strike',
            None)
        contract_type = str(work_dict.get(
            'contract',
            'C')).upper()
        label = work_dict.get(
            'label',
            label)
        iex_datasets = work_dict.get(
            'iex_datasets',
            iex_consts.DEFAULT_FETCH_DATASETS)
        td_datasets = work_dict.get(
            'td_datasets',
            td_consts.DEFAULT_FETCH_DATASETS_TD)
        fetch_mode = work_dict.get(
            'fetch_mode',
            ae_consts.FETCH_MODE_ALL)
        iex_token = work_dict.get(
            'iex_token',
            iex_consts.IEX_TOKEN)
        td_token = work_dict.get(
            'td_token',
            td_consts.TD_TOKEN)
        str_fetch_mode = str(fetch_mode).lower()
        backfill_date = work_dict.get(
            'backfill_date',
            None)
        verbose = work_dict.get(
            'verbose',
            False)

        # control flags to deal with feed issues:
        get_iex_data = True
        get_td_data = True

        if (
                fetch_mode == ae_consts.FETCH_MODE_ALL
                or str_fetch_mode == 'initial'):
            get_iex_data = True
            get_td_data = True
            iex_datasets = ae_consts.IEX_INITIAL_DATASETS
        elif (
                fetch_mode == ae_consts.FETCH_MODE_ALL
                or str_fetch_mode == 'all'):
            get_iex_data = True
            get_td_data = True
            iex_datasets = ae_consts.IEX_DATASETS_DEFAULT
        elif (
                fetch_mode == ae_consts.FETCH_MODE_YHO
                or str_fetch_mode == 'yahoo'):
            get_iex_data = False
            get_td_data = False
        elif (
                fetch_mode == ae_consts.FETCH_MODE_IEX
                or str_fetch_mode == 'iex-all'):
            get_iex_data = True
            get_td_data = False
            iex_datasets = ae_consts.IEX_DATASETS_DEFAULT
        elif (
                fetch_mode == ae_consts.FETCH_MODE_IEX
                or str_fetch_mode == 'iex'):
            get_iex_data = True
            get_td_data = False
            iex_datasets = ae_consts.IEX_INTRADAY_DATASETS
        elif (
                fetch_mode == ae_consts.FETCH_MODE_INTRADAY
                or str_fetch_mode == 'intra'):
            get_iex_data = True
            get_td_data = True
            iex_datasets = ae_consts.IEX_INTRADAY_DATASETS
        elif (
                fetch_mode == ae_consts.FETCH_MODE_DAILY
                or str_fetch_mode == 'daily'):
            get_iex_data = True
            get_td_data = False
            iex_datasets = ae_consts.IEX_DAILY_DATASETS
        elif (
                fetch_mode == ae_consts.FETCH_MODE_WEEKLY
                or str_fetch_mode == 'weekly'):
            get_iex_data = True
            get_td_data = False
            iex_datasets = ae_consts.IEX_WEEKLY_DATASETS
        elif (
                fetch_mode == ae_consts.FETCH_MODE_TD
                or str_fetch_mode == 'td'):
            get_iex_data = False
            get_td_data = True
        else:
            get_iex_data = False
            get_td_data = False

            fetch_arr = str_fetch_mode.split(',')
            found_fetch = False
            iex_datasets = []
            for fetch_name in fetch_arr:
                if fetch_name not in iex_datasets:
                    if fetch_name == 'iex_min':
                        iex_datasets.append('minute')
                    elif fetch_name == 'min':
                        iex_datasets.append('minute')
                    elif fetch_name == 'minute':
                        iex_datasets.append('minute')
                    elif fetch_name == 'day':
                        iex_datasets.append('daily')
                    elif fetch_name == 'daily':
                        iex_datasets.append('daily')
                    elif fetch_name == 'iex_day':
                        iex_datasets.append('daily')
                    elif fetch_name == 'quote':
                        iex_datasets.append('quote')
                    elif fetch_name == 'iex_quote':
                        iex_datasets.append('quote')
                    elif fetch_name == 'iex_stats':
                        iex_datasets.append('stats')
                    elif fetch_name == 'stats':
                        iex_datasets.append('stats')
                    elif fetch_name == 'peers':
                        iex_datasets.append('peers')
                    elif fetch_name == 'iex_peers':
                        iex_datasets.append('peers')
                    elif fetch_name == 'news':
                        iex_datasets.append('news')
                    elif fetch_name == 'iex_news':
                        iex_datasets.append('news')
                    elif fetch_name == 'fin':
                        iex_datasets.append('financials')
                    elif fetch_name == 'iex_fin':
                        iex_datasets.append('financials')
                    elif fetch_name == 'earn':
                        iex_datasets.append('earnings')
                    elif fetch_name == 'iex_earn':
                        iex_datasets.append('earnings')
                    elif fetch_name == 'div':
                        iex_datasets.append('dividends')
                    elif fetch_name == 'iex_div':
                        iex_datasets.append('dividends')
                    elif fetch_name == 'comp':
                        iex_datasets.append('company')
                    elif fetch_name == 'iex_comp':
                        iex_datasets.append('company')
                    elif fetch_name == 'td':
                        get_td_data = True
                    else:
                        log.warn(
                            'unsupported IEX dataset '
                            f'{fetch_name}')
            found_fetch = (
                len(iex_datasets) != 0)
            if not found_fetch:
                log.error(
                    f'{label} - unsupported '
                    f'fetch_mode={fetch_mode} value')
            else:
                get_iex_data = True
                log.debug(
                    f'{label} - '
                    f'fetching={len(iex_datasets)} '
                    f'{iex_datasets} '
                    f'fetch_mode={fetch_mode}')
        # end of screening custom fetch_mode settings

        num_tokens = 0

        if get_iex_data:
            if not iex_token:
                log.warn(
                    f'{label} - '
                    'please set a valid IEX Cloud Account token ('
                    'https://iexcloud.io/cloud-login/#/register'
                    ') to fetch data from IEX Cloud. It must be '
                    'set as an environment variable like: '
                    'export IEX_TOKEN=<token>')
                get_iex_data = False
            else:
                num_tokens += 1
        # sanity check - disable IEX fetch if the token is not set
        if get_td_data:
            missing_td_token = [
                'MISSING_TD_TOKEN',
                'SETYOURTDTOKEN',
                'SETYOURTRADIERTOKENHERE'
            ]
            if td_token in missing_td_token:
                log.warn(
                    f'{label} - '
                    'please set a valid Tradier Account token ('
                    'https://developer.tradier.com/user/sign_up'
                    ') to fetch pricing data from Tradier. It must be '
                    'set as an environment variable like: '
                    'export TD_TOKEN=<token>')
                get_td_data = False
            else:
                num_tokens += 1
        # sanity check - disable Tradier fetch if the token is not set

        """
        as of Thursday, Jan. 3, 2019:
        https://developer.yahoo.com/yql/
        Important EOL Notice: As of Thursday, Jan. 3, 2019
        the YQL service at query.yahooapis.com will be retired
        """
        get_yahoo_data = False

        if (
                not get_iex_data and
                not get_td_data and
                not get_yahoo_data):
            err = None
            if num_tokens == 0:
                res['status'] = ae_consts.MISSING_TOKEN
                err = (
                    f'Please set a valid IEX_TOKEN or TD_TOKEN '
                    f'environment variable')
            else:
                err = (
                    f'Please set at least one supported datafeed from '
                    f'either: '
                    f'IEX Cloud (fetch -t TICKER -g iex) or '
                    f'Tradier (fetch -t TICKER -g td) '
                    f'for '
                    f'ticker={ticker} '
                    f'cur_date={cur_date} '
                    f'IEX enabled={get_iex_data} '
                    f'TD enabled={get_td_data} '
                    f'YHO enabled={get_yahoo_data}')
                res['status'] = ae_consts.ERR
                res['err'] = err
            return get_task_results.get_task_results(
                work_dict=work_dict,
                result=res)
        # end of checking that there is at least 1 feed on

        if not exp_date:
            exp_date = opt_dates.option_expiration(
                date=exp_date)
        else:
            exp_date = datetime.datetime.strptime(
                exp_date,
                '%Y-%m-%d')

        rec['updated'] = cur_date.strftime('%Y-%m-%d %H:%M:%S')
        log.debug(
            f'{label} getting pricing for ticker={ticker} '
            f'cur_date={cur_date} exp_date={exp_date} '
            f'IEX={get_iex_data} '
            f'TD={get_td_data} '
            f'YHO={get_yahoo_data}')

        yahoo_rec = {
            'ticker': ticker,
            'pricing': None,
            'options': None,
            'calls': None,
            'puts': None,
            'news': None,
            'exp_date': None,
            'publish_pricing_update': None,
            'date': None,
            'updated': None
        }

        # disabled on 2019-01-03
        if get_yahoo_data:
            log.debug(f'{label} YHO ticker={ticker}')
            yahoo_res = yahoo_data.get_data_from_yahoo(
                work_dict=work_dict)
            status_str = ae_consts.get_status(status=yahoo_res['status'])
            if yahoo_res['status'] == ae_consts.SUCCESS:
                yahoo_rec = yahoo_res['rec']
                msg = (
                    f'{label} YHO ticker={ticker} '
                    f'redis_key={redis_key}_[price,news,options] '
                    f'status={status_str} err={yahoo_res["err"]}')
                if ae_consts.ev('SHOW_SUCCESS', '0') == '1':
                    log.info(msg)
                else:
                    log.debug(msg)
                rec['pricing'] = yahoo_rec.get('pricing', '{}')
                rec['news'] = yahoo_rec.get('news', '{}')
                rec['options'] = yahoo_rec.get('options', '{}')
                rec['calls'] = rec['options'].get(
                    'calls', ae_consts.EMPTY_DF_STR)
                rec['puts'] = rec['options'].get(
                    'puts', ae_consts.EMPTY_DF_STR)
                num_success += 1
            else:
                log.error(
                    f'{label} failed YHO ticker={ticker} '
                    f'status={status_str} err={yahoo_res["err"]}')
        # end of get from yahoo

        if get_iex_data:
            num_iex_ds = len(iex_datasets)
            log.debug(f'{label} IEX datasets={num_iex_ds}')
            for idx, ft_type in enumerate(iex_datasets):
                dataset_field = iex_consts.get_ft_str(
                    ft_type=ft_type)

                log.debug(
                    f'{label} IEX={idx}/{num_iex_ds} '
                    f'field={dataset_field} ticker={ticker}')
                iex_label = f'{label}-{dataset_field}'
                iex_req = copy.deepcopy(work_dict)
                iex_req['label'] = iex_label
                iex_req['ft_type'] = ft_type
                iex_req['field'] = dataset_field
                iex_req['ticker'] = ticker
                iex_req['backfill_date'] = backfill_date
                iex_req['verbose'] = verbose

                iex_res = iex_data.get_data_from_iex(
                    work_dict=iex_req)

                status_str = (
                    ae_consts.get_status(status=iex_res['status']))
                if iex_res['status'] == ae_consts.SUCCESS:
                    iex_rec = iex_res['rec']
                    rk = f'{redis_key}_{dataset_field}'
                    if backfill_date:
                        rk = (
                            f'{ticker}_{backfill_date}_'
                            f'{dataset_field}')
                    msg = (
                        f'{label} IEX ticker={ticker} '
                        f'redis_key={rk} '
                        f'field={dataset_field} '
                        f'status={status_str} '
                        f'err={iex_res["err"]}')
                    if ae_consts.ev('SHOW_SUCCESS', '0') == '1':
                        log.info(msg)
                    else:
                        log.debug(msg)
                    if dataset_field == 'news':
                        rec['iex_news'] = iex_rec['data']
                    else:
                        rec[dataset_field] = iex_rec['data']
                    num_success += 1
                else:
                    log.debug(
                        f'{label} failed IEX ticker={ticker} '
                        f'field={dataset_field} '
                        f'status={status_str} err={iex_res["err"]}')
                # end of if/else succcess
            # end idx, ft_type in enumerate(iex_datasets):
        # end of if get_iex_data

        if get_td_data:
            num_td_ds = len(td_datasets)

            latest_pricing = None
            try:
                latest_pricing = iex_pricing.get_pricing_on_date(
                    ticker=ticker,
                    date_str=None,
                    label=label)
            except Exception as e:
                log.critical(
                    f'failed to get {ticker} iex latest pricing data '
                    f'with ex={e}')
            # end of trying to extract the latest pricing data from redis

            log.debug(
                f'{label} TD datasets={num_td_ds} '
                f'pricing={latest_pricing}')

            for idx, ft_type in enumerate(td_datasets):
                dataset_field = td_consts.get_ft_str_td(
                    ft_type=ft_type)
                log.debug(
                    f'{label} TD={idx}/{num_td_ds} '
                    f'field={dataset_field} ticker={ticker}')
                td_label = (
                    f'{label}-{dataset_field}')
                td_req = copy.deepcopy(work_dict)
                td_req['label'] = td_label
                td_req['ft_type'] = ft_type
                td_req['field'] = dataset_field
                td_req['ticker'] = ticker
                td_req['latest_pricing'] = latest_pricing
                td_res = td_data.get_data_from_td(
                    work_dict=td_req)

                status_str = (
                    ae_consts.get_status(status=td_res['status']))
                if td_res['status'] == ae_consts.SUCCESS:
                    td_rec = td_res['rec']
                    msg = (
                        f'{label} TD ticker={ticker} '
                        f'redis_key={redis_key}_{dataset_field} '
                        f'field={dataset_field} '
                        f'status={status_str} '
                        f'err={td_res["err"]}')
                    if ae_consts.ev('SHOW_SUCCESS', '0') == '1':
                        log.info(msg)
                    else:
                        log.debug(msg)
                    if dataset_field == 'tdcalls':
                        rec['tdcalls'] = td_rec['data']
                    if dataset_field == 'tdputs':
                        rec['tdputs'] = td_rec['data']
                    else:
                        rec[dataset_field] = td_rec['data']
                    num_success += 1
                else:
                    log.critical(
                        f'{label} failed TD ticker={ticker} '
                        f'field={dataset_field} '
                        f'status={status_str} err={td_res["err"]}')
                # end of if/else succcess
            # end idx, ft_type in enumerate(td_datasets):
        # end of if get_td_data

        rec['num_success'] = num_success

        update_req = {
            'data': rec
        }
        update_req['ticker'] = ticker
        update_req['ticker_id'] = ticker_id
        update_req['strike'] = cur_strike
        update_req['contract'] = contract_type
        update_req['s3_enabled'] = work_dict.get(
            's3_enabled',
            ae_consts.ENABLED_S3_UPLOAD)
        update_req['redis_enabled'] = work_dict.get(
            'redis_enabled',
            ae_consts.ENABLED_REDIS_PUBLISH)
        update_req['s3_bucket'] = s3_bucket
        update_req['s3_key'] = s3_key
        update_req['s3_access_key'] = work_dict.get(
            's3_access_key',
            ae_consts.S3_ACCESS_KEY)
        update_req['s3_secret_key'] = work_dict.get(
            's3_secret_key',
            ae_consts.S3_SECRET_KEY)
        update_req['s3_region_name'] = work_dict.get(
            's3_region_name',
            ae_consts.S3_REGION_NAME)
        update_req['s3_address'] = work_dict.get(
            's3_address',
            ae_consts.S3_ADDRESS)
        update_req['s3_secure'] = work_dict.get(
            's3_secure',
            ae_consts.S3_SECURE)
        update_req['redis_key'] = redis_key
        update_req['redis_address'] = work_dict.get(
            'redis_address',
            ae_consts.REDIS_ADDRESS)
        update_req['redis_password'] = work_dict.get(
            'redis_password',
            ae_consts.REDIS_PASSWORD)
        update_req['redis_db'] = int(work_dict.get(
            'redis_db',
            ae_consts.REDIS_DB))
        update_req['redis_expire'] = work_dict.get(
            'redis_expire',
            ae_consts.REDIS_EXPIRE)
        update_req['updated'] = rec['updated']
        update_req['label'] = label
        update_req['celery_disabled'] = True
        update_status = ae_consts.NOT_SET

        if backfill_date:
            update_req['redis_key'] = (
                f'{ticker}_{backfill_date}')
            update_req['s3_key'] = (
                f'{ticker}_{backfill_date}')

        try:
            update_res = publisher.run_publish_pricing_update(
                work_dict=update_req)
            update_status = update_res.get(
                'status',
                ae_consts.NOT_SET)
            status_str = ae_consts.get_status(status=update_status)
            if ae_consts.ev('DEBUG_RESULTS', '0') == '1':
                log.debug(
                    f'{label} update_res '
                    f'status={status_str} '
                    f'data={ae_consts.ppj(update_res)}')
            else:
                log.debug(
                    f'{label} run_publish_pricing_update '
                    f'status={status_str}')
            # end of if/else

            rec['publish_pricing_update'] = update_res
            res = build_result.build_result(
                status=ae_consts.SUCCESS,
                err=None,
                rec=rec)
        except Exception as f:
            err = (
                f'{label} publisher.run_publish_pricing_update failed '
                f'with ex={f}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
        # end of trying to publish results to connected services

    except Exception as e:
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=(
                'failed - get_new_pricing_data '
                f'dict={work_dict} with ex={e}'),
            rec=rec)
        log.error(
            f'{label} - {res["err"]}')
    # end of try/ex

    if ae_consts.ev('DATASET_COLLECTION_SLACK_ALERTS', '0') == '1':
        env_name = 'DEV'
        if ae_consts.ev('PROD_SLACK_ALERTS', '1') == '1':
            env_name = 'PROD'
        done_msg = (
            f'Dataset collected ticker=*{ticker}* on '
            f'env=*{env_name}* '
            f'redis_key={redis_key} s3_key={s3_key} '
            f'IEX={get_iex_data} '
            f'TD={get_td_data} '
            f'YHO={get_yahoo_data}')
        log.debug(f'{label} sending slack msg={done_msg}')
        if res['status'] == ae_consts.SUCCESS:
            slack_utils.post_success(
                msg=done_msg,
                block=False,
                jupyter=True)
        else:
            slack_utils.post_failure(
                msg=done_msg,
                block=False,
                jupyter=True)
        # end of if/else success
    # end of publishing to slack

    log.debug(
        'task - get_new_pricing_data done - '
        f'{label} - status={ae_consts.get_status(res["status"])}')

    return get_task_results.get_task_results(
        work_dict=work_dict,
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

    log.debug(f'run_get_new_pricing_data - {label} - start')

    response = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    # allow running without celery
    if ae_consts.is_celery_disabled(
            work_dict=work_dict):
        work_dict['celery_disabled'] = True
        task_res = get_new_pricing_data(
            work_dict)
        if task_res:
            response = task_res.get(
                'result',
                task_res)
            if ae_consts.ev('DEBUG_RESULTS', '0') == '1':
                response_details = response
                try:
                    response_details = ae_consts.ppj(response)
                except Exception:
                    response_details = response

                log.debug(
                    f'{label} task result={response_details}')
        else:
            log.error(
                f'{label} celery was disabled but the task={response} '
                'did not return anything')
        # end of if response
    else:
        task_res = get_new_pricing_data.delay(
            work_dict=work_dict)
        rec = {
            'task_id': task_res
        }
        response = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)
    # if celery enabled

    if response:
        status_str = ae_consts.get_status(response['status'])
        if ae_consts.ev('DEBUG_RESULTS', '0') == '1':
            log.debug(
                f'run_get_new_pricing_data - {label} - done '
                f'status={status_str} '
                f'err={response["err"]} '
                f'rec={response["rec"]}')
        else:
            log.debug(
                f'run_get_new_pricing_data - {label} - done '
                f'status={status_str} '
                f'rec={response["rec"]}')
    else:
        log.debug(
            f'run_get_new_pricing_data - {label} - done '
            'no response')
    # end of if/else response

    return response
# end of run_get_new_pricing_data
