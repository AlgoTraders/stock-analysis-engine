"""
Extract an TD dataset from Redis (S3 support coming soon) and
load it into a ``pandas.DataFrame``

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

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.dataset_scrub_utils as scrub_utils
import analysis_engine.get_data_from_redis_key as redis_get
import analysis_engine.td.consts as td_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def extract_option_calls_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_option_calls_dataset

    Extract the TD options calls for a ticker and
    return it as a ``pandas.Dataframe``

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_option_dataset('calls', work_dict, scrub_mode=scrub_mode)
# end of extract_option_calls_dataset


def extract_option_puts_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_option_puts_dataset

    Extract the TD options puts for a ticker and
    return it as a ``pandas.Dataframe``

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_option_dataset('puts', work_dict, scrub_mode=scrub_mode)
# end of extract_option_puts_dataset


def extract_option_dataset(
        option,
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_option_dataset

    Extract the TD options puts/calls for a ticker and
    return it as a ``pandas.Dataframe``

    :param option: either 'calls' or 'puts' option type
    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    if not option or option not in ['calls', 'puts']:
        return ae_consts.NOT_RUN, None

    label = f'{work_dict.get("label", "extract")}'
    ds_id = work_dict.get('ticker')
    df_type = (
        td_consts.DATAFEED_TD_PUTS if option == 'puts'
        else td_consts.DATAFEED_TD_CALLS)
    df_str = td_consts.get_datafeed_str_td(df_type=df_type)
    redis_key = work_dict.get(
        'redis_key',
        work_dict.get('tdputs', 'missing-redis-key'))
    s3_key = work_dict.get(
        's3_key',
        work_dict.get('tdputs', 'missing-s3-key'))
    redis_host = work_dict.get(
        'redis_host',
        None)
    redis_port = work_dict.get(
        'redis_port',
        None)
    redis_db = work_dict.get(
        'redis_db',
        ae_consts.REDIS_DB)
    verbose = work_dict.get(
        'verbose_td',
        False)

    if verbose:
        log.info(
            f'{label} - {df_str} - start - redis_key={redis_key} '
            f's3_key={s3_key}')

    if not redis_host and not redis_port:
        redis_host = ae_consts.REDIS_ADDRESS.split(':')[0]
        redis_port = ae_consts.REDIS_ADDRESS.split(':')[1]

    exp_date_str = None
    options_df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=work_dict.get('password', None),
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        if verbose:
            log.info(
                f'{label} - {df_str} redis get data key={redis_key} '
                f'status={ae_consts.get_status(status=status)}')

        if status == ae_consts.SUCCESS:
            options_json = None
            if f'{option}' in redis_rec['rec']['data']:
                options_json = redis_rec['rec']['data'][f'{option}']
            else:
                options_json = redis_rec['rec']['data']
            if verbose:
                log.info(f'{label} - {df_str} redis convert {option} to df')
            try:
                options_df = pd.read_json(
                    options_json,
                    orient='records')
                if len(options_df.index) == 0:
                    return ae_consts.SUCCESS, None
                if 'date' not in options_df:
                    log.debug(
                        f'failed to find date column in TD {option} '
                        f'df={options_df} len={len(options_df.index)}')
                    return ae_consts.SUCCESS, None
                options_df.sort_values(
                        by=[
                            'date',
                            'strike'
                        ])
                """
                for i, r in calls_df.iterrows():
                    print(r['date'])
                convert_epochs = [
                    'ask_date',
                    'bid_date',
                    'trade_date'
                ]
                for c in convert_epochs:
                    if c in options_df:
                        options_df[c] = pd.DatetimeIndex(pd.to_datetime(
                            options_df[c],
                            format=ae_consts.COMMON_TICK_DATE_FORMAT
                        )).tz_localize(
                            'UTC').tz_convert(
                                'US/Eastern')
                # dates converted
                """
                exp_date_str = (
                    options_df['exp_date'].iloc[-1])

                options_df['date'] = options_df['date'].dt.strftime(
                    ae_consts.COMMON_TICK_DATE_FORMAT)

            except Exception:
                log.debug(
                    f'{label} - {df_str} redis_key={redis_key} '
                    f'no {option} df found')
                return ae_consts.EMPTY, None
            # end of try/ex to convert to df
            if verbose:
                log.info(
                    f'{label} - {df_str} redis_key={redis_key} {option}='
                    f'{len(options_df.index)} exp_date={exp_date_str}')
        else:
            if verbose:
                log.info(
                    f'{label} - {df_str} did not find valid redis '
                    f'option {option} in redis_key={redis_key} '
                    f'status={ae_consts.get_status(status=status)}')

    except Exception as e:
        log.debug(
            f'{label} - {df_str} - ds_id={ds_id} failed getting option '
            f'{option} from redis={redis_host}:{redis_port}@{redis_db} '
            f'key={redis_key} ex={e}')
        return ae_consts.ERR, None
    # end of try/ex extract from redis

    if verbose:
        log.info(
            f'{label} - {df_str} ds_id={ds_id} extract scrub={scrub_mode}')

    scrubbed_df = scrub_utils.extract_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=df_type,
        msg_format='df={} date_str={}',
        ds_id=ds_id,
        df=options_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_option_dataset
