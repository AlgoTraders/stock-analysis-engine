"""
Work in progress - screener-driven analysis task

**Supported environment variables**

::

    export DEBUG_RESULTS=1

"""

import os
import analysis_engine.get_task_results as task_utils
import analysis_engine.fetch as fetch_utils
import analysis_engine.build_result as build_result
import analysis_engine.finviz.fetch_api as finviz_utils
import analysis_engine.work_tasks.custom_task as use_task_class
from celery.task import task
from analysis_engine.consts import is_celery_disabled
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import IEX_DATASETS_DEFAULT
from analysis_engine.consts import get_status
from analysis_engine.consts import ev
from analysis_engine.consts import ppj
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


@task(
    bind=True,
    base=use_task_class.CustomTask,
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

    log.info(
        '{} - start'.format(
            label))

    rec = {}
    res = build_result.build_result(
        status=NOT_RUN,
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
            status=ERR,
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
            IEX_DATASETS_DEFAULT))

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
            '{} fetch={} tickers={} '
            'iex_datasets={} '
            'sell_task={} '
            'buy_task={}'.format(
                label,
                fetch_mode,
                tickers,
                iex_datasets,
                determine_sells_callback,
                determine_buys_callback))

        """
        Input - Set up required urls for building buckets
        """
        fv_urls = work_dict.get(
            'urls',
            )

        if not fv_urls:
            res = build_result.build_result(
                status=ERR,
                err='missing required urls list of screeners',
                rec=rec)

        # stop if something errored out with the
        # celery helper for turning off celery to debug
        # without an engine running
        if res['err']:
            log.error(
                '{} - tickers={} fetch={} iex_datasets={} '
                'hit validation err={}'.format(
                    label,
                    tickers,
                    fetch_mode,
                    iex_datasets,
                    res['err']))

            return task_utils.get_task_results(
                work_dict=work_dict,
                result=res)
        # end of input validation checks

        num_urls = len(fv_urls)
        log.info(
            '{} - running urls={}'.format(
                label,
                fv_urls))

        fv_dfs = []
        for uidx, url in enumerate(fv_urls):
            log.info(
                '{} - url={}/{} url={}'.format(
                    label,
                    uidx,
                    num_urls,
                    url))
            fv_res = finviz_utils.fetch_tickers_from_screener(
                url=url)
            if fv_res['status'] == SUCCESS:
                fv_dfs.append(fv_res['rec']['data'])
                for ft_tick in fv_res['rec']['tickers']:
                    upper_ft_ticker = ft_tick.upper()
                    if upper_ft_ticker not in tickers:
                        tickers.append(upper_ft_ticker)
                # end of for all found tickers
            else:
                log.error(
                    '{} - failed url={}/{} url={}'.format(
                        label,
                        uidx,
                        num_urls,
                        url))
            # if success vs log the error
        # end of urls to get pandas.DataFrame and unique tickers

        """
        Find tickers in screens
        """

        num_tickers = len(tickers)

        log.info(
            '{} - fetching tickers={} from urls={}'.format(
                label,
                num_tickers,
                num_urls))

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
                status=SUCCESS,
                err=None,
                rec=rec)
        else:
            err = (
                '{} - tickers={} failed fetch={} '
                'iex_datasets={}'.format(
                    label,
                    tickers,
                    fetch_mode,
                    iex_datasets))
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)

        log.info(
            '{} - done'.format(
                label))
    except Exception as e:
        err = (
            '{} - tickers={} fetch={} hit ex={} '.format(
                label,
                tickers,
                fetch_mode,
                e))
        log.error(err)
        res = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex

    return task_utils.get_task_results(
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
    label = '{} - {}'.format(
        fn_name,
        work_dict.get(
            'label',
            ''))

    log.info(
        '{} - start'.format(
            label))

    response = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    # allow running without celery
    if is_celery_disabled(
            work_dict=work_dict):
        work_dict['celery_disabled'] = True
        task_res = task_screener_analysis(
            work_dict)
        if task_res:
            response = task_res.get(
                'result',
                task_res)
            if ev('DEBUG_RESULTS', '0') == '1':
                response_details = response
                try:
                    response_details = ppj(response)
                except Exception:
                    response_details = response

                log.info(
                    '{} task result={}'.format(
                        label,
                        response_details))
        else:
            log.error(
                '{} celery was disabled but the task={} '
                'did not return anything'.format(
                    label,
                    response))
        # end of if response
    else:
        task_res = task_screener_analysis.delay(
            work_dict=work_dict)
        rec = {
            'task_id': task_res
        }
        response = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)
    # if celery enabled

    if response:
        if ev('DEBUG_RESULTS', '0') == '1':
            log.info(
                '{} - done '
                'status={} err={} rec={}'.format(
                    label,
                    get_status(response['status']),
                    response['err'],
                    response['rec']))
        else:
            log.info(
                '{} - done '
                'status={} err={}'.format(
                    label,
                    get_status(response['status']),
                    response['err']))
    else:
        log.info(
            '{} - done '
            'no response'.format(
                label))
    # end of if/else response

    return response
# end of run_screener_analysis
