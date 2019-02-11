"""
Work in progress - screener-driven analysis task

**Supported environment variables**

::

    export DEBUG_RESULTS=1

"""

import os
import celery.task as celery_task
import analysis_engine.consts as ae_consts
import analysis_engine.get_task_results as get_task_results
import analysis_engine.fetch as fetch_utils
import analysis_engine.build_result as build_result
import analysis_engine.finviz.fetch_api as finviz_utils
import analysis_engine.work_tasks.custom_task as custom_task
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


@celery_task(
    bind=True,
    base=custom_task.CustomTask,
    queue='task_screener_analysis')
def task_screener_analysis(
        self,
        work_dict):
    """task_screener_analysis

    :param work_dict: task dictionary
    """

    label = work_dict.get(
        'label',
        'screener')

    log.info(f'{label} - start')

    rec = {}
    res = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    """
    Input - Set up dataset sources to collect
    """

    ticker = work_dict.get(
        'ticker',
        None)
    org_tickers = work_dict.get(
        'tickers',
        None)

    if not ticker and not org_tickers:
        res = build_result.build_result(
            status=ae_consts.ERR,
            err='missing ticker or tickers',
            rec=rec)

    tickers = []
    if not org_tickers:
        if ticker:
            tickers = [
                ticker
            ]
    else:
        for t in org_tickers:
            upper_cased_ticker = str(t).upper()
            if upper_cased_ticker not in tickers:
                tickers.append(upper_cased_ticker)
        # build a unique ticker list
    # end of ensuring tickers is a unique list of
    # upper-cased ticker symbol strings

    # fetch from: 'all', 'iex' or 'yahoo'
    fetch_mode = work_dict.get(
        'fetch_mode',
        os.getenv(
            'FETCH_MODE',
            'iex'))
    iex_datasets = work_dict.get(
        'iex_datasets',
        os.getenv(
            'IEX_DATASETS_DEFAULT',
            ae_consts.IEX_DATASETS_DEFAULT))

    # if defined, these are task functions for
    # calling customiized determine Celery tasks
    determine_sells_callback = work_dict.get(
        'determine_sells',
        None)
    determine_buys_callback = work_dict.get(
        'determine_buys',
        None)

    try:

        log.info(
            f'{label} fetch={fetch_mode} tickers={tickers} '
            f'iex_datasets={iex_datasets} '
            f'sell_task={determine_sells_callback} '
            f'buy_task={determine_buys_callback}')

        """
        Input - Set up required urls for building buckets
        """
        fv_urls = work_dict.get(
            'urls',
            )

        if not fv_urls:
            res = build_result.build_result(
                status=ae_consts.ERR,
                err='missing required urls list of screeners',
                rec=rec)

        # stop if something errored out with the
        # celery helper for turning off celery to debug
        # without an engine running
        if res['err']:
            log.error(
                f'{label} - tickers={tickers} fetch={fetch_mode} '
                f'iex_datasets={iex_datasets} hit validation err={res["err"]}')

            return get_task_results.get_task_results(
                work_dict=work_dict,
                result=res)
        # end of input validation checks

        num_urls = len(fv_urls)
        log.info(f'{label} - running urls={fv_urls}')

        fv_dfs = []
        for uidx, url in enumerate(fv_urls):
            log.info(
                f'{label} - url={uidx}/{num_urls} url={url}')
            fv_res = finviz_utils.fetch_tickers_from_screener(
                url=url)
            if fv_res['status'] == ae_consts.SUCCESS:
                fv_dfs.append(fv_res['rec']['data'])
                for ft_tick in fv_res['rec']['tickers']:
                    upper_ft_ticker = ft_tick.upper()
                    if upper_ft_ticker not in tickers:
                        tickers.append(upper_ft_ticker)
                # end of for all found tickers
            else:
                log.error(f'{label} - failed url={uidx}/{num_urls} url={url}')
            # if success vs log the error
        # end of urls to get pandas.DataFrame and unique tickers

        """
        Find tickers in screens
        """

        num_tickers = len(tickers)

        log.info(
            f'{label} - fetching tickers={num_tickers} from urls={num_urls}')

        """
        pull ticker data
        """

        fetch_recs = fetch_utils.fetch(
            tickers=tickers,
            fetch_mode=fetch_mode,
            iex_datasets=iex_datasets)

        if fetch_recs:
            rec = fetch_recs

            """
            Output - Where is data getting cached and archived?
            (this helps to retroactively evaluate trading performance)
            """

            res = build_result.build_result(
                status=ae_consts.SUCCESS,
                err=None,
                rec=rec)
        else:
            err = (
                f'{label} - tickers={ticker} failed fetch={fetch_mode} '
                f'iex_datasets={iex_datasets}')
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)

        log.info(f'{label} - done')
    except Exception as e:
        err = (
            f'{label} - tickers={tickers} fetch={fetch_mode} hit ex={e} ')
        log.error(err)
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex

    return get_task_results.get_task_results(
        work_dict=work_dict,
        result=res)
# end of task_screener_analysis


def run_screener_analysis(
        work_dict):
    """run_screener_analysis

    Celery wrapper for running without celery

    :param work_dict: task data
    """

    fn_name = 'run_screener_analysis'
    label = f'''{fn_name} - {work_dict.get(
        'label',
        '')}'''

    log.info(f'{label} - start')

    response = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    # allow running without celery
    if ae_consts.is_celery_disabled(
            work_dict=work_dict):
        work_dict['celery_disabled'] = True
        task_res = task_screener_analysis(
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

                log.info(
                    f'{label} task result={response_details}')
        else:
            log.error(
                f'{label} celery was disabled but the task={response} '
                'did not return anything')
        # end of if response
    else:
        task_res = task_screener_analysis.delay(
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
        if ae_consts.ev('DEBUG_RESULTS', '0') == '1':
            log.info(
                f'{label} - done '
                f'status={ae_consts.get_status(response["status"])} '
                f'err={response["err"]} rec={response["rec"]}')
        else:
            log.info(
                f'{label} - done '
                f'status={ae_consts.get_status(response["status"])} '
                f'err={response["err"]}')
    else:
        log.info(f'{label} - done no response')
    # end of if/else response

    return response
# end of run_screener_analysis
