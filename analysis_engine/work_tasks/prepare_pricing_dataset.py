"""
**Prepare Pricing Dataset**

Prepare dataset for analysis. This task collapses
nested json dictionaries into a
csv file with a header row and stores the output
file in s3 and redis automatically.

- if key not in redis, load the key by the same name from s3
- prepare dataset from redis key
- the dataset will be stored as a dictionary with a pandas dataframe

**Sample work_dict request for this method**

`analysis_engine.api_requests.build_prepare_dataset_request <https://
github.com/AlgoTraders/stock-analysis-engine/blob/master/
analysis_engine/api_requests.py#L300>`__

::

    work_request = {
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

**Supported Environment Variables**

::

    export DEBUG_PREPARE=1
    export DEBUG_RESULTS=1

"""

import datetime
import redis
import celery.task as celery_task
import analysis_engine.consts as ae_consts
import analysis_engine.build_result as build_result
import analysis_engine.api_requests as api_requests
import analysis_engine.get_data_from_redis_key as redis_get
import analysis_engine.get_task_results as get_task_results
import analysis_engine.work_tasks.custom_task as custom_task
import analysis_engine.work_tasks.publish_from_s3_to_redis as s3_to_redis
import analysis_engine.dict_to_csv as dict_to_csv
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


@celery_task(
    bind=True,
    base=custom_task.CustomTask,
    queue='prepare_pricing_dataset')
def prepare_pricing_dataset(
        self,
        work_dict):
    """prepare_pricing_dataset

    Prepare dataset for analysis. Supports loading dataset from
    s3 if not found in redis. Outputs prepared artifact as a csv
    to s3 and redis.

    :param work_dict: dictionary for key/values
    """

    label = 'prepare'

    log.info(f'task - {label} - start work_dict={work_dict}')

    initial_data = None

    ticker = ae_consts.TICKER
    ticker_id = ae_consts.TICKER_ID
    rec = {
        'ticker': None,
        'ticker_id': None,
        's3_enabled': True,
        'redis_enabled': True,
        's3_bucket': None,
        's3_key': None,
        'redis_key': None,
        'prepared_s3_key': None,
        'prepared_s3_bucket': None,
        'prepared_redis_key': None,
        'prepared_data': None,
        'prepared_size': None,
        'initial_data': None,
        'initial_size': None,
        'ignore_columns': None,
        'updated': None
    }
    res = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    try:
        ticker = work_dict.get(
            'ticker',
            ae_consts.TICKER)
        ticker_id = int(work_dict.get(
            'ticker_id',
            ae_consts.TICKER_ID))

        if not ticker:
            res = build_result.build_result(
                status=ae_consts.ERR,
                err='missing ticker',
                rec=rec)
            return res

        label = work_dict.get(
            'label',
            label)
        s3_key = work_dict.get(
            's3_key',
            None)
        s3_bucket_name = work_dict.get(
            's3_bucket',
            'pricing')
        s3_access_key = work_dict.get(
            's3_access_key',
            ae_consts.S3_ACCESS_KEY)
        s3_secret_key = work_dict.get(
            's3_secret_key',
            ae_consts.S3_SECRET_KEY)
        s3_region_name = work_dict.get(
            's3_region_name',
            ae_consts.S3_REGION_NAME)
        s3_address = work_dict.get(
            's3_address',
            ae_consts.S3_ADDRESS)
        s3_secure = work_dict.get(
            's3_secure',
            ae_consts.S3_SECURE) == '1'
        redis_address = work_dict.get(
            'redis_address',
            ae_consts.REDIS_ADDRESS)
        redis_key = work_dict.get(
            'redis_key',
            ae_consts.REDIS_KEY)
        redis_password = work_dict.get(
            'redis_password',
            ae_consts.REDIS_PASSWORD)
        redis_db = work_dict.get(
            'redis_db',
            None)
        if not redis_db:
            redis_db = ae_consts.REDIS_DB
        redis_expire = None
        if 'redis_expire' in work_dict:
            redis_expire = work_dict.get(
                'redis_expire',
                ae_consts.REDIS_EXPIRE)
        updated = work_dict.get(
            'updated',
            datetime.datetime.utcnow().strftime(
                '%Y_%m_%d_%H_%M_%S'))
        prepared_s3_key = work_dict.get(
            'prepared_s3_key',
            f'{ticker}_{updated}.csv')
        prepared_s3_bucket = work_dict.get(
            'prepared_s3_bucket',
            'prepared')
        prepared_redis_key = work_dict.get(
            'prepared_redis_key',
            'prepared')
        ignore_columns = work_dict.get(
            'ignore_columns',
            None)
        log.info(
            f'{label} redis enabled address={redis_address}@{redis_db} '
            f'key={redis_key} '
            f'prepare_s3={prepared_s3_bucket}:{prepared_s3_key} '
            f'prepare_redis={prepared_redis_key} '
            f'ignore_columns={ignore_columns}')
        redis_host = redis_address.split(':')[0]
        redis_port = redis_address.split(':')[1]

        enable_s3 = True
        enable_redis_publish = True

        rec['ticker'] = ticker
        rec['ticker_id'] = ticker_id
        rec['s3_bucket'] = s3_bucket_name
        rec['s3_key'] = s3_key
        rec['redis_key'] = redis_key
        rec['prepared_s3_key'] = prepared_s3_key
        rec['prepared_s3_bucket'] = prepared_s3_bucket
        rec['prepared_redis_key'] = prepared_redis_key
        rec['updated'] = updated
        rec['s3_enabled'] = enable_s3
        rec['redis_enabled'] = enable_redis_publish

        try:
            log.info(
                f'{label} connecting redis={redis_host}:{redis_port} '
                f'db={redis_db} key={redis_key} '
                f'updated={updated} expire={redis_expire}')
            rc = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db)
        except Exception as e:
            err = (
                f'{label} failed - redis connection to '
                f'address={redis_address}@{redis_port} '
                f'db={redis_db} key={redis_key} ex={e}')
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        # end of try/ex for connecting to redis

        initial_data_res = redis_get.get_data_from_redis_key(
            label=label,
            client=rc,
            key=redis_key)

        log.info(
            f'{label} get redis key={redis_key} '
            f'status={ae_consts.get_status(initial_data_res["status"])} '
            f'err={initial_data_res["err"]}')

        initial_data = initial_data_res['rec'].get(
            'data',
            None)

        if enable_s3 and not initial_data:

            log.info(
                f'{label} failed to find redis_key={redis_key} trying s3 from '
                f's3_key={s3_key} s3_bucket={s3_bucket_name} '
                f's3_address={s3_address}')

            get_from_s3_req = \
                api_requests.build_publish_from_s3_to_redis_request()

            get_from_s3_req['s3_enabled'] = enable_s3
            get_from_s3_req['s3_access_key'] = s3_access_key
            get_from_s3_req['s3_secret_key'] = s3_secret_key
            get_from_s3_req['s3_region_name'] = s3_region_name
            get_from_s3_req['s3_address'] = s3_address
            get_from_s3_req['s3_secure'] = s3_secure
            get_from_s3_req['s3_key'] = s3_key
            get_from_s3_req['s3_bucket'] = s3_bucket_name
            get_from_s3_req['redis_key'] = redis_key
            get_from_s3_req['label'] = f'{label}-run_publish_from_s3_to_redis'

            log.info(f'{label} load from s3={s3_key} to redis={redis_key}')

            try:
                # run in synchronous mode:
                get_from_s3_req['celery_disabled'] = True
                task_res = s3_to_redis.run_publish_from_s3_to_redis(
                    get_from_s3_req)
                if task_res.get(
                        'status',
                        ae_consts.ERR) == ae_consts.SUCCESS:
                    log.info(
                        f'{label} loaded s3={s3_bucket_name}:{s3_key} '
                        f'to redis={redis_key} retrying')
                    initial_data_res = redis_get.get_data_from_redis_key(
                        label=label,
                        client=rc,
                        key=redis_key)

                    log.info(
                        f'{label} get redis try=2 key={redis_key} status='
                        f'{ae_consts.get_status(initial_data_res["status"])} '
                        f'err={initial_data_res["err"]}')

                    initial_data = initial_data_res['rec'].get(
                        'data',
                        None)
                else:
                    err = (
                        f'{label} ERR failed loading from '
                        f'bucket={s3_bucket_name} s3_key={s3_key} to '
                        f'redis_key={redis_key} with res={task_res}')
                    log.error(err)
                    res = build_result.build_result(
                        status=ae_consts.ERR,
                        err=err,
                        rec=rec)
                    return res
            except Exception as e:
                err = (
                    f'{label} extract from s3 and publish to redis failed '
                    f'loading data from bucket={s3_bucket_name} in '
                    f's3_key={s3_key} with publish to redis_key={redis_key} '
                    f'with ex={e}')
                log.error(err)
                res = build_result.build_result(
                    status=ae_consts.ERR,
                    err=err,
                    rec=rec)
                return res
            # end of try/ex for publishing from s3->redis
        # end of if enable_s3

        if not initial_data:
            err = (
                f'{label} did not find any data to prepare in '
                f'redis_key={redis_key} or s3_key={s3_key} in '
                f'bucket={s3_bucket_name}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res

        initial_data_num_chars = len(str(initial_data))
        initial_size_value = None
        initial_size_str = None
        if initial_data_num_chars < ae_consts.PREPARE_DATA_MIN_SIZE:
            err = (
                f'{label} not enough data={initial_data_num_chars} in '
                f'redis_key={redis_key} or s3_key={s3_key} in '
                f'bucket={s3_bucket_name}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        else:
            initial_size_value = initial_data_num_chars / 1024000
            initial_size_str = ae_consts.to_f(initial_size_value)
            if ae_consts.ev('DEBUG_PREPARE', '0') == '1':
                log.info(
                    f'{label} initial - redis_key={redis_key} '
                    f'data={str(initial_data)}')
            else:
                log.info(
                    f'{label} initial - redis_key={redis_key} data '
                    f'size={initial_size_str} MB')
        # end of trying to get initial_data

        rec['initial_data'] = initial_data
        rec['initial_size'] = initial_data_num_chars

        prepare_data = None

        try:
            if ae_consts.ev('DEBUG_PREPARE', '0') == '1':
                log.info(
                    f'{label} data={ae_consts.ppj(initial_data)} - flatten - '
                    f'{initial_size_str} MB from redis_key={redis_key}')
            else:
                log.info(
                    f'{label} flatten - {initial_size_str} MB from '
                    f'redis_key={redis_key}')
            prepare_data = dict_to_csv.flatten_dict(
                data=initial_data)
        except Exception as e:
            prepare_data = None
            err = (
                f'{label} flatten - convert to csv failed with ex={e} '
                f'redis_key={redis_key}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        # end of try/ex

        if not prepare_data:
            err = (
                f'{label} flatten - did not return any data from '
                f'redis_key={redis_key} or s3_key={s3_key} in '
                f'bucket={s3_bucket_name}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        # end of prepare_data

        prepare_data_num_chars = len(str(prepare_data))
        prepare_size_value = None

        if prepare_data_num_chars < ae_consts.PREPARE_DATA_MIN_SIZE:
            err = (
                f'{label} prepare - there is not enough '
                f'data={prepare_data_num_chars} in redis_key={redis_key}')
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        else:
            prepare_size_value = prepare_data_num_chars / 1024000
            prepare_size_str = ae_consts.to_f(prepare_size_value)
            if ae_consts.ev('DEBUG_PREPARE', '0') == '1':
                log.info(
                    f'{label} data={redis_key} - prepare - '
                    f'redis_key={ae_consts.ppj(prepare_data)}')
            else:
                log.info(
                    f'{label} prepare - redis_key={redis_key} data '
                    f'size={prepare_size_str} MB')
        # end of trying to the size of the prepared data

        rec['prepared_data'] = prepare_data
        rec['prepared_size'] = prepare_data_num_chars

        res = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

        rc = None

    except Exception as e:
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=(
                'failed - prepare_pricing_dataset '
                f'dict={work_dict} with ex={e}'),
            rec=rec)
        log.error(f'{label} - {res["err"]}')
    # end of try/ex

    log.info(
        'task - prepare_pricing_dataset done - '
        f'{label} - status={ae_consts.get_status(res["status"])}')

    return get_task_results.get_task_results(
        work_dict=work_dict,
        result=res)
# end of prepare_pricing_dataset


def run_prepare_pricing_dataset(
        work_dict):
    """run_prepare_pricing_dataset

    Celery wrapper for running without celery

    :param work_dict: task data
    """

    label = work_dict.get(
        'label',
        '')

    log.info(f'run_prepare_pricing_dataset - {label} - start')

    response = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec={})
    task_res = {}

    # allow running without celery
    if ae_consts.is_celery_disabled(
            work_dict=work_dict):
        work_dict['celery_disabled'] = True
        task_res = prepare_pricing_dataset(
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
                log.info(f'{label} task result={response_details}')
        else:
            log.error(
                f'{label} celery was disabled but the task={response} '
                'did not return anything')
        # end of if response
    else:
        task_res = prepare_pricing_dataset.delay(
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
                f'run_prepare_pricing_dataset - {label} - done '
                f'status={ae_consts.get_status(response["status"])} '
                f'err={response["err"]} rec={response["rec"]}')
        else:
            log.info(
                f'run_prepare_pricing_dataset - {label} - done '
                f'status={ae_consts.get_status(response["status"])} '
                f'err={response["err"]}')
    else:
        log.info(
            f'run_prepare_pricing_dataset - {label} - done '
            'no response')
    # end of if/else response

    return response
# end of run_prepare_pricing_dataset
