"""
Extract an TD dataset from Redis (S3 support coming soon) and
load it into a ``pandas.DataFrame``

Supported environment variables:

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.dataset_scrub_utils as scrub_utils
import analysis_engine.get_data_from_redis_key as redis_get
import analysis_engine.td.consts as td_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def extract_option_calls_dataset(
        ticker=None,
        date=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """extract_option_calls_dataset

    Extract the TD options calls for a ticker and
    return a tuple (status, ``pandas.Dataframe``)

    .. code-block:: python

        import analysis_engine.td.extract_df_from_redis as td_extract

        # extract by historical date is also supported as an arg
        # date='2019-02-15'
        calls_status, calls_df = td_extract.extract_option_calls_dataset(
            ticker='SPY')
        print(calls_df)

    :param ticker: string ticker to extract
    :param date: optional - string date to extract
        formatted ``YYYY-MM-DD``
    :param work_dict: dictionary of args
    :param scrub_mode: optional - string type of
        scrubbing handler to run
    :param verbose: optional - boolean for turning on logging
    """
    label = 'extract_td_calls'
    latest_close_date = ae_utils.get_last_close_str()
    use_date = date
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = f'{work_dict.get("label", label)}'
    if not use_date:
        use_date = latest_close_date

    ds_id = ticker
    df_type = td_consts.DATAFEED_TD_CALLS
    df_str = td_consts.get_datafeed_str_td(df_type=df_type)
    redis_db = ae_consts.REDIS_DB
    redis_key = f'{ticker}_{use_date}_tdcalls'
    redis_host, redis_port = ae_consts.get_redis_host_and_port(
        req=work_dict)
    redis_password = ae_consts.REDIS_PASSWORD
    s3_key = redis_key

    if work_dict:
        redis_db = work_dict.get(
            'redis_db',
            redis_db)
        redis_password = work_dict.get(
            'redis_password',
            redis_password)
        verbose = work_dict.get(
            'verbose_td',
            verbose)

    if verbose:
        log.info(
            f'{label} - {df_str} - start - redis_key={redis_key} '
            f's3_key={s3_key}')

    exp_date_str = None
    calls_df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        if verbose:
            log.info(
                f'{label} - {df_str} redis get data key={redis_key} '
                f'status={ae_consts.get_status(status=status)}')

        if status == ae_consts.SUCCESS:
            calls_json = None
            if 'tdcalls' in redis_rec['rec']['data']:
                calls_json = redis_rec['rec']['data']['tdcalls']
            elif 'calls' in redis_rec['rec']['data']:
                calls_json = redis_rec['rec']['data']['calls']
            else:
                calls_json = redis_rec['rec']['data']
            if not calls_json:
                return ae_consts.SUCCESS, pd.DataFrame([])
            if verbose:
                log.info(f'{label} - {df_str} redis convert calls to df')
            exp_date_str = None
            try:
                calls_df = pd.read_json(
                    calls_json,
                    orient='records')
                if len(calls_df.index) == 0:
                    return ae_consts.SUCCESS, pd.DataFrame([])
                if 'date' not in calls_df:
                    if verbose:
                        log.error(
                            'failed to find date column in TD calls '
                            f'df={calls_df} from lens={len(calls_df.index)}')
                    return ae_consts.SUCCESS, pd.DataFrame([])
                calls_df.sort_values(
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
                    if c in calls_df:
                        calls_df[c] = pd.DatetimeIndex(pd.to_datetime(
                            calls_df[c],
                            format=ae_consts.COMMON_TICK_DATE_FORMAT
                        )).tz_localize(
                            'UTC').tz_convert(
                                'US/Eastern')
                # dates converted
                """
                exp_date_str = (
                    calls_df['exp_date'].iloc[-1])

                calls_df['date'] = calls_df['date'].dt.strftime(
                    ae_consts.COMMON_TICK_DATE_FORMAT)

            except Exception as f:
                not_fixed = True
                if (
                        'Can only use .dt accessor with '
                        'datetimelike values') in str(f):
                    try:
                        log.critical(
                            f'fixing dates in {redis_key}')
                        # remove epoch second data and
                        # use only the millisecond date values
                        bad_date = ae_consts.EPOCH_MINIMUM_DATE
                        calls_df['date'][
                            calls_df['date'] < bad_date] = None
                        calls_df = calls_df.dropna(axis=0, how='any')
                        fmt = ae_consts.COMMON_TICK_DATE_FORMAT
                        calls_df['date'] = pd.to_datetime(
                            calls_df['date'],
                            unit='ms').dt.strftime(fmt)
                        not_fixed = False
                    except Exception as g:
                        log.critical(
                            f'failed to parse date column {calls_df["date"]} '
                            f'with dt.strftime ex={f} and EPOCH EX={g}')
                        return ae_consts.SUCCESS, pd.DataFrame([])
                # if able to fix error or not

                if not_fixed:
                    log.debug(
                        f'{label} - {df_str} redis_key={redis_key} '
                        f'no calls df found or ex={f}')
                    return ae_consts.SUCCESS, pd.DataFrame([])
                # if unable to fix - return out

                log.error(
                    f'{label} - {df_str} redis_key={redis_key} '
                    f'no calls df found or ex={f}')
                return ae_consts.SUCCESS, pd.DataFrame([])
            # end of try/ex to convert to df
            if verbose:
                log.info(
                    f'{label} - {df_str} redis_key={redis_key} '
                    f'calls={len(calls_df.index)} exp_date={exp_date_str}')
        else:
            if verbose:
                log.info(
                    f'{label} - {df_str} did not find valid redis '
                    f'option calls in redis_key={redis_key} '
                    f'status={ae_consts.get_status(status=status)}')

    except Exception as e:
        if verbose:
            log.error(
                f'{label} - {df_str} - ds_id={ds_id} failed getting option '
                f'calls from redis={redis_host}:{redis_port}@{redis_db} '
                f'key={redis_key} ex={e}')
        return ae_consts.ERR, pd.DataFrame([])
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
        df=calls_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_option_calls_dataset


def extract_option_puts_dataset(
        ticker=None,
        date=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """extract_option_puts_dataset

    Extract the TD options puts for a ticker and
    return a tuple (status, ``pandas.Dataframe``)

    .. code-block:: python

        import analysis_engine.td.extract_df_from_redis as td_extract

        # extract by historical date is also supported as an arg
        # date='2019-02-15'
        puts_status, puts_df = td_extract.extract_option_puts_dataset(
            ticker='SPY')
        print(puts_df)

    :param ticker: string ticker to extract
    :param date: optional - string date to extract
        formatted ``YYYY-MM-DD``
    :param work_dict: dictionary of args
    :param scrub_mode: optional - string type of
        scrubbing handler to run
    :param verbose: optional - boolean for turning on logging
    """
    label = 'extract_td_puts'
    latest_close_date = ae_utils.get_last_close_str()
    use_date = date
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = f'{work_dict.get("label", label)}'
    if not use_date:
        use_date = latest_close_date

    ds_id = ticker
    df_type = td_consts.DATAFEED_TD_PUTS
    df_str = td_consts.get_datafeed_str_td(df_type=df_type)
    redis_db = ae_consts.REDIS_DB
    redis_key = f'{ticker}_{use_date}_tdputs'
    redis_host, redis_port = ae_consts.get_redis_host_and_port(
        req=work_dict)
    redis_password = ae_consts.REDIS_PASSWORD
    s3_key = redis_key

    if work_dict:
        redis_db = work_dict.get(
            'redis_db',
            redis_db)
        redis_password = work_dict.get(
            'redis_password',
            redis_password)
        verbose = work_dict.get(
            'verbose_td',
            verbose)

    if verbose:
        log.info(
            f'{label} - {df_str} - start - redis_key={redis_key} '
            f's3_key={s3_key}')

    exp_date_str = None
    puts_df = None
    status = ae_consts.NOT_RUN
    try:
        redis_rec = redis_get.get_data_from_redis_key(
            label=label,
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            key=redis_key,
            decompress_df=True)

        status = redis_rec['status']
        if verbose:
            log.info(
                f'{label} - {df_str} redis get data key={redis_key} '
                f'status={ae_consts.get_status(status=status)}')

        if status == ae_consts.SUCCESS:
            puts_json = None
            if 'tdputs' in redis_rec['rec']['data']:
                puts_json = redis_rec['rec']['data']['tdputs']
            if 'puts' in redis_rec['rec']['data']:
                puts_json = redis_rec['rec']['data']['puts']
            else:
                puts_json = redis_rec['rec']['data']
            if not puts_json:
                return ae_consts.SUCCESS, pd.DataFrame([])
            if verbose:
                log.info(f'{label} - {df_str} redis convert puts to df')
            try:
                puts_df = pd.read_json(
                    puts_json,
                    orient='records')
                if len(puts_df.index) == 0:
                    return ae_consts.SUCCESS, pd.DataFrame([])
                if 'date' not in puts_df:
                    log.debug(
                        'failed to find date column in TD puts '
                        f'df={puts_df} len={len(puts_df.index)}')
                    return ae_consts.SUCCESS, pd.DataFrame([])
                puts_df.sort_values(
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
                    if c in puts_df:
                        puts_df[c] = pd.DatetimeIndex(pd.to_datetime(
                            puts_df[c],
                            format=ae_consts.COMMON_TICK_DATE_FORMAT
                        )).tz_localize(
                            'UTC').tz_convert(
                                'US/Eastern')
                # dates converted
                """
                exp_date_str = (
                    puts_df['exp_date'].iloc[-1])

                puts_df['date'] = puts_df['date'].dt.strftime(
                    ae_consts.COMMON_TICK_DATE_FORMAT)

            except Exception:
                log.debug(
                    f'{label} - {df_str} redis_key={redis_key} '
                    'no puts df found')
                return ae_consts.SUCCESS, pd.DataFrame([])
            # end of try/ex to convert to df
            if verbose:
                log.info(
                    f'{label} - {df_str} redis_key={redis_key} '
                    f'puts={len(puts_df.index)} exp_date={exp_date_str}')
        else:
            if verbose:
                log.info(
                    f'{label} - {df_str} did not find valid redis '
                    f'option puts in redis_key={redis_key} '
                    f'status={ae_consts.get_status(status=status)}')

    except Exception as e:
        if verbose:
            log.error(
                f'{label} - {df_str} - ds_id={ds_id} failed getting option '
                f'puts from redis={redis_host}:{redis_port}@{redis_db} '
                f'key={redis_key} ex={e}')
        return ae_consts.ERR, pd.DataFrame([])
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
        df=puts_df)

    status = ae_consts.SUCCESS

    return status, scrubbed_df
# end of extract_option_puts_dataset
