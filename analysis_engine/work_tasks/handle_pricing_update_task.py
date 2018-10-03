"""
Handle Pricing Update Task
==========================

Get the latest stock news, quotes and options chains for a
ticker and publish the values to redis and S3 for downstream analysis.

Writes pricing updates to S3 and Redis by
building a list of publishing sub-task:

Sample work_dict request for this method
----------------------------------------

`analysis_engine.api_requests.publish_pricing_update <https://
github.com/AlgoTraders/stock-analysis-engine/blob/master/ana
lysis_engine/api_requests.py#L218>`__

::

    work = {
        'ticker': ticker,
        'ticker_id': ticker_id,
        's3_bucket': s3_bucket_name,
        's3_key': s3_key,
        'redis_key': redis_key,
        'prepared_s3_key': s3_prepared_key,
        'prepared_s3_bucket': s3_prepared_bucket_name,
        'prepared_redis_key': redis_prepared_key,
        'ignore_columns': ignore_columns,
        's3_enabled': s3_enabled,
        'redis_enabled': redis_enabled
    }

.. tip:: This task uses the `analysis_engine.work_tasks.
    custom_task.CustomTask class <https://github.com/A
    lgoTraders/stock-analysis-engine/blob/master/anal
    ysis_engine/work_tasks/custom_task.py>`__ for
    task event handling.
"""

import datetime
import analysis_engine.get_task_results
import analysis_engine.work_tasks.custom_task
import analysis_engine.build_result as build_result
import analysis_engine.work_tasks.publish_pricing_update as \
    publisher
import analysis_engine.options_dates
import analysis_engine.get_pricing
from celery.task import task
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import TICKER
from analysis_engine.consts import get_status
from analysis_engine.consts import is_celery_disabled
from analysis_engine.consts import ppj

log = build_colorized_logger(
    name=__name__)


@task(
    bind=True,
    base=analysis_engine.work_tasks.custom_task.CustomTask,
    queue='handle_pricing_update_task')
def handle_pricing_update_task(
        self,
        work_dict):
    """handle_pricing_update_task

    Writes pricing updates to S3 and Redis

    :param work_dict: dictionary for key/values
    """

    label = 'update_prices'

    log.info(
        'task - {} - start'.format(
            label))

    ticker = TICKER
    ticker_id = 1
    rec = {
        'ticker': None,
        'ticker_id': None,
        'pricing_s3_bucket': None,
        'pricing_s3_key': None,
        'pricing_size': None,
        'pricing_redis_key': None,
        'news_s3_bucket': None,
        'news_s3_key': None,
        'news_size': None,
        'news_redis_key': None,
        'options_s3_bucket': None,
        'options_s3_key': None,
        'options_size': None,
        'options_redis_key': None
    }
    res = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:
        ticker = work_dict.get(
            'ticker',
            TICKER)
        ticker_id = int(work_dict.get(
            'ticker_id',
            1))

        rec['ticker'] = ticker
        rec['ticker_id'] = ticker_id

        pricing_data = work_dict['pricing']
        news_data = work_dict['news']
        options_data = work_dict['options']
        updated = work_dict['updated']
        label = work_dict.get(
            'label',
            label)

        cur_date = datetime.datetime.utcnow()
        cur_date_str = cur_date.strftime(
            '%Y_%m_%d_%H_%M_%S')

        pricing_s3_key = work_dict.get(
            'pricing_s3_key',
            'pricing_ticker_{}_id_{}_date_{}'.format(
                ticker,
                ticker_id,
                cur_date_str))
        news_s3_key = work_dict.get(
            'news_s3_key',
            'news_ticker_{}_id_{}_date_{}'.format(
                ticker,
                ticker_id,
                cur_date_str))
        options_s3_key = work_dict.get(
            'options_s3_key',
            'options_ticker_{}_id_{}_date_{}'.format(
                ticker,
                ticker_id,
                cur_date_str))

        pricing_s3_bucket = work_dict.get(
            'pricing_s3_bucket',
            'pricing')
        news_s3_bucket = work_dict.get(
            'news_s3_bucket',
            'news')
        options_s3_bucket = work_dict.get(
            'options_s3_bucket',
            'options')

        pricing_by_ticker_redis_key = work_dict.get(
            'pricing_redis_key',
            'price_{}'.format(
                ticker))
        news_by_ticker_redis_key = work_dict.get(
            'news_redis_key',
            'news_{}'.format(
                ticker))
        options_by_ticker_redis_key = work_dict.get(
            'options_redis_key',
            'options_{}'.format(
                ticker))

        pricing_size = len(str(
            pricing_data))
        news_size = len(str(
            news_data))
        options_size = len(str(
            options_data))

        payloads_to_publish = [
            {
                'ticker': ticker,
                'ticker_id': ticker_id,
                's3_bucket': pricing_s3_bucket,
                's3_key': pricing_s3_key,
                'data': pricing_data,
                'redis_key': pricing_by_ticker_redis_key,
                'size': pricing_size,
                'updated': updated,
                'label': label
            },
            {
                'ticker': ticker,
                'ticker_id': ticker_id,
                's3_bucket': options_s3_bucket,
                's3_key': options_s3_key,
                'data': options_data,
                'redis_key': options_by_ticker_redis_key,
                'size': options_size,
                'updated': updated,
                'label': label
            },
            {
                'ticker': ticker,
                'ticker_id': ticker_id,
                's3_bucket': news_s3_bucket,
                's3_key': news_s3_key,
                'data': news_data,
                'redis_key': news_by_ticker_redis_key,
                'size': news_size,
                'updated': updated,
                'label': label
            }
        ]

        rec['pricing_s3_bucket'] = pricing_s3_bucket
        rec['pricing_s3_key'] = pricing_s3_key
        rec['pricing_redis_key'] = pricing_by_ticker_redis_key
        rec['news_s3_bucket'] = news_s3_bucket
        rec['news_s3_key'] = news_s3_key
        rec['news_redis_key'] = news_by_ticker_redis_key
        rec['options_s3_bucket'] = options_s3_bucket
        rec['options_s3_key'] = options_s3_bucket
        rec['options_redis_key'] = options_by_ticker_redis_key

        total_payloads = len(payloads_to_publish)

        log.info(
            '{} ticker={} processing payloads={}'.format(
                label,
                ticker,
                total_payloads))

        for ridx, r in enumerate(payloads_to_publish):
            log.info(
                '{} ticker={} update={}/{} key={} redis_key={}'.format(
                    label,
                    ticker,
                    ridx,
                    total_payloads,
                    r['s3_key'],
                    r['redis_key']))
            r['celery_disabled'] = False
            r['label'] = 'handle_pricing_update_task-{}'.format(
                label)
            payload_res = \
                publisher.task_publish_pricing_update(
                    work_dict=r)
            log.info(
                '{} ticker={} update={}/{} status={} '
                's3_key={} redis_key={}'.format(
                    label,
                    ticker,
                    ridx,
                    total_payloads,
                    get_status(status=payload_res['status']),
                    r['s3_key'],
                    r['redis_key']))
        # end of for all payloads to publish

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - handle_pricing_update_task '
                'dict={} with ex={}').format(
                    work_dict,
                    e),
            rec=rec)
        log.error(
            '{} - {}'.format(
                label,
                res['err']))
    # end of try/ex

    log.info(
        'task - handle_pricing_update_task done - '
        '{} - status={}'.format(
            label,
            get_status(res['status'])))

    return analysis_engine.get_task_results.get_task_results(
        work_dict=work_dict,
        result=res)
# end of handle_pricing_update_task


def run_handle_pricing_update_task(
        work_dict):
    """run_handle_pricing_update_task

    Celery wrapper for running without celery

    :param work_dict: task data
    """

    label = work_dict.get(
        'label',
        '')

    log.info(
        'run_handle_pricing_update_task - {} - start'.format(
            label))

    response = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    log.info(
        'run_handle_pricing_update_task - {} - done '
        'status={} err={} rec={}'.format(
            label,
            get_status(response['status']),
            response['err'],
            response['rec']))

    # allow running without celery
    if is_celery_disabled(
            work_dict=work_dict):
        work_dict['celery_disabled'] = True
        task_res = handle_pricing_update_task(
            work_dict)
        if task_res:
            response = task_res.get(
                'result',
                task_res)
            response_details = response
            try:
                response_details = ppj(response)
            except Exception:
                response_details = response
            log.info(
                'getting task result={}'.format(
                    response_details))
        else:
            log.error(
                '{} celery was disabled but the task={} '
                'did not return anything'.format(
                    label,
                    response))
        # end of if response
    else:
        task_res = handle_pricing_update_task.delay(
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
        log.info(
            'run_handle_pricing_update_task - {} - done '
            'status={} err={} rec={}'.format(
                label,
                get_status(response['status']),
                response['err'],
                response['rec']))
    else:
        log.info(
            'run_handle_pricing_update_task - {} - done '
            'no response'.format(
                label))
    # end of if/else response

    return response
# end of run_handle_pricing_update_task
