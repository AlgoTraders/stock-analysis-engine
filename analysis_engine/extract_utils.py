"""

Dataset Extraction Utilities
============================

Helper for extracting a dataset from Redis or S3 and
load it into a ``pandas.DataFrame``. This was designed
to ignore the source of the dataset (IEX vs Yahoo) and
perform the extract and load operations without
knowledge of the underlying dataset.

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_EXTRACT=1

    # verbose logging for just Redis operations in this module
    export DEBUG_REDIS_EXTRACT=1

    # verbose logging for just S3 operations in this module
    export DEBUG_S3_EXTRACT=1

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import analysis_engine.consts as ae_consts
import analysis_engine.build_df_from_redis as build_df
import analysis_engine.dataset_scrub_utils as scrub_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def perform_extract(
        df_type,
        df_str,
        work_dict,
        dataset_id_key='ticker',
        scrub_mode='sort-by-date'):
    """perform_extract

    Helper for extracting from Redis or S3

    :param df_type: datafeed type enum
    :param ds_str: dataset string name
    :param work_dict: incoming work request dictionary
    :param dataset_id_key: configurable dataset identifier
                           key for tracking scrubbing and
                           debugging errors
    :param scrub_mode: scrubbing mode on extraction for
                       one-off cleanup before analysis
    """
    status = ae_consts.FAILED
    ds_id = work_dict.get(
        dataset_id_key,
        None)
    label = work_dict.get(
        'label',
        'extract')
    s3_bucket = work_dict.get(
        's3_bucket',
        ae_consts.S3_BUCKET)
    s3_key = work_dict.get(
        's3_key',
        ae_consts.S3_KEY)
    redis_key = work_dict.get(
        'redis_key',
        ae_consts.REDIS_KEY)
    s3_enabled = work_dict.get(
        's3_enabled',
        ae_consts.ENABLED_S3_UPLOAD)
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
        ae_consts.S3_SECURE)
    redis_address = work_dict.get(
        'redis_address',
        ae_consts.REDIS_ADDRESS)
    redis_password = work_dict.get(
        'redis_password',
        ae_consts.REDIS_PASSWORD)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)
    redis_expire = work_dict.get(
        'redis_expire',
        ae_consts.REDIS_EXPIRE)

    log.debug(
        '{} - {} - START - ds_id={} scrub_mode={} '
        'redis_address={}@{} redis_key={} '
        's3={} s3_address={} s3_bucket={} s3_key={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode,
            redis_address,
            redis_db,
            redis_key,
            s3_enabled,
            s3_address,
            s3_bucket,
            s3_key))

    if ae_consts.ev('DEBUG_REDIS_EXTRACT', '0') == '1':
        log.info(
            '{} - {} - ds_id={} redis '
            'pw={} expire={}'.format(
                label,
                df_str,
                ds_id,
                redis_password,
                redis_expire))

    if ae_consts.ev('DEBUG_S3_EXTRACT', '0') == '1':
        log.info(
            '{} - {} - ds_id={} s3 '
            'ak={} sk={} region={} secure={}'.format(
                label,
                df_str,
                ds_id,
                s3_access_key,
                s3_secret_key,
                s3_region_name,
                s3_secure))

    extract_res = None
    try:
        extract_res = build_df.build_df_from_redis(
            label=label,
            address=redis_address,
            db=redis_db,
            key=redis_key)
    except Exception as e:
        extract_res = None
        log.error(
            '{} - {} - ds_id={} failed extract from '
            'redis={}@{} key={} ex={}'.format(
                label,
                df_str,
                ds_id,
                redis_address,
                redis_db,
                redis_key,
                e))
    # end of try/ex extract from redis

    if not extract_res:
        return status, None

    valid_df = (
        extract_res['status'] == ae_consts.SUCCESS
        and extract_res['rec']['valid_df'])

    if not valid_df:
        if ae_consts.ev('DEBUG_S3_EXTRACT', '0') == '1':
            log.error(
                '{} - {} ds_id={} invalid df '
                'status={} extract_res={}'.format(
                    label,
                    df_str,
                    ds_id,
                    ae_consts.get_status(
                        status=extract_res['status']),
                    extract_res))
        return status, None

    extract_df = extract_res['rec']['data']

    log.debug(
        '{} - {} ds_id={} extract scrub={}'.format(
            label,
            df_str,
            ds_id,
            scrub_mode))

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=extract_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of perform_extract
