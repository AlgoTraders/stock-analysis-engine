"""
Work in progress - screener-driven analysis task
"""

import os
import analysis_engine.get_task_results
import analysis_engine.fetch as fetch_utils
import analysis_engine.build_result as build_result
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import IEX_DATASETS_DEFAULT
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def run_screener_analysis(
        work_dict):
    """run_screener_analysis

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

    try:

        log.info(
            '{} fetch={} tickers={} '
            'iex_datasets={}'.format(
                label,
                fetch_mode,
                tickers,
                iex_datasets))

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

            return analysis_engine.get_task_results.get_task_results(
                work_dict=work_dict,
                result=res)
        # end of input validation checks

        """
        Output - Where is data getting cached and archived?
        """

        """
        Find tickers in screens
        """

        num_tickers = len(tickers)
        num_urls = len(fv_urls)

        log.info(
            '{} - pulling tickers={} from urls={}'.format(
                label,
                num_urls))

        found_tickers = []
        for fidx, url in enumerate(fv_urls):


        log.info(
            '{} - found uniq_tickers={} from urls={}'.format(
                label,
                len(uniq_tickers),
                num_urls))

        """
        pull ticker data
        """

        fetch_res = fetch_utils.fetch(
            tickers=tickers,
            fetch_mode=fetch_mode,
            iex_datasets=iex_datasets)

        if fetch_res['status'] == SUCCESS:
            rec = fetch_res['rec']
            res = build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
        else:
            err = (
                '{} - tickers={} failed fetch={} '
                'iex_datasets={} status={} err={}'.format(
                    label,
                    tickers,
                    fetch_mode,
                    iex_datasets,
                    get_status(status=fetch_res['status']),
                    fetch_res['err']))
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

    return analysis_engine.get_task_results.get_task_results(
        work_dict=work_dict,
        result=res)
# end of run_screener_analysis


if __name__ == '__main__':
    run_screener_analysis()
