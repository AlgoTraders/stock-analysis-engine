"""
Fetch data from Tradier:
https://developer.tradier.com/getting_started
"""

import json
import copy
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.td.consts as td_consts
import analysis_engine.options_dates as opt_dates
import analysis_engine.td.fetch_api as td_fetch
import analysis_engine.td.extract_df_from_redis as td_extract
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def fetch_data(
        work_dict,
        fetch_type=None):
    """fetch_data

    Factory method for fetching data from
    TD using an enum or string alias. Returns
    a pandas ``DataFrame`` and only supports
    one ticker at a time.

    Supported enums from: ``analysis_engine.td.consts``

    ::

        fetch_type = FETCH_TD_CALLS
        fetch_type = FETCH_TD_PUTS

    Supported ``work_dict['ft_type']`` string values:

    ::

        work_dict['ft_type'] = 'tdcalls'
        work_dict['ft_type'] = 'tdputs'

    :param work_dict: dictionary of args for the Tradier api
    :param fetch_type: optional - name or enum of the fetcher to create
                       can also be a lower case string
                       in work_dict['ft_type']
    """
    use_fetch_name = None
    ticker = work_dict.get(
        'ticker',
        None)
    if not fetch_type:
        fetch_type = work_dict.get(
            'ft_type',
            None)
    if fetch_type:
        use_fetch_name = str(fetch_type).lower()

    if 'exp_date' not in work_dict:
        work_dict['exp_date'] = opt_dates.option_expiration().strftime(
            ae_consts.COMMON_DATE_FORMAT)

    log.debug(
        'name={} type={} args={}'.format(
            use_fetch_name,
            fetch_type,
            work_dict))

    status_df = ae_consts.NOT_SET
    df = pd.DataFrame([{}])

    if (
            use_fetch_name == 'tdcalls' or
            fetch_type == td_consts.FETCH_TD_CALLS):
        status_df, fetch_df = td_fetch.fetch_calls(
            work_dict=work_dict)

        if status_df == ae_consts.SUCCESS:
            log.info(
                'call - merge df')
            work_copy = copy.deepcopy(
                work_dict)
            work_copy['ft_type'] = td_consts.FETCH_TD_CALLS
            work_copy['fd_type'] = 'tdcalls'
            if 'tdcalls' in work_dict:
                work_copy['redis_key'] = work_dict['tdcalls']
                work_copy['s3_key'] = '{}.json'.format(
                    work_dict['tdcalls'])
            else:
                work_copy['redis_key'] = (
                    '{}_tdcalls'.format(
                        work_dict['redis_key']))
                work_copy['s3_key'] = (
                    '{}_tdcalls'.format(
                        work_dict['s3_key']))
            ext_status, ext_df = \
                td_extract.extract_option_calls_dataset(
                    work_dict=work_copy)
            if ext_status == ae_consts.SUCCESS and len(ext_df.index) > 0:
                log.info(
                    'call - merging fetch={} with ext={}'.format(
                        len(fetch_df.index),
                        len(ext_df.index)))
                """
                for testing compression:
                """
                """
                import sys
                print(ext_df['date'])
                print(ext_df['ask_date'])
                print(ext_df['bid_date'])
                print(ext_df['trade_date'])
                sys.exit(1)
                """
                extracted_records = json.loads(ext_df.to_json(
                    orient='records'))
                fetched_records = json.loads(fetch_df.to_json(
                    orient='records'))
                new_records = []
                dates_by_strike_dict = {}
                for ex_row in extracted_records:
                    date_strike_name = (
                        '{}_{}'.format(
                            ex_row['created'],
                            ex_row['strike']))
                    if date_strike_name not in dates_by_strike_dict:
                        new_node = {}
                        for c in td_consts.TD_OPTION_COLUMNS:
                            if c in ex_row:
                                new_node[c] = ex_row[c]
                        # end of for all columns to copy over
                        new_node.pop('index', None)
                        new_node.pop('level_0', None)
                        new_records.append(new_node)
                        dates_by_strike_dict[date_strike_name] = True
                # build extracted records

                for ft_row in fetched_records:
                    date_strike_name = (
                        '{}_{}'.format(
                            ft_row['created'],
                            ft_row['strike']))
                    try:
                        if date_strike_name not in dates_by_strike_dict:
                            new_node = {}
                            for c in td_consts.TD_OPTION_COLUMNS:
                                if c in ft_row:
                                    new_node[c] = ft_row[c]
                            # end of for all columns to copy over
                            new_node.pop('index', None)
                            new_node.pop('level_0', None)
                            new_records.append(new_node)
                            dates_by_strike_dict[date_strike_name] = True
                        else:
                            log.error(
                                'already have {} call - date={} '
                                'strike={}'.format(
                                    ticker,
                                    ft_row['created'],
                                    ft_row['strike']))
                    except Exception as p:
                        log.critical(
                            'failed fetching call with ex={}'.format(
                                p))
                        return ae_consts.ERR, None
                    # end of adding fetched records after the extracted

                df = pd.DataFrame(new_records)
                df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
                log.info(
                    'call - merged={}'.format(
                        len(df.index)))
            else:
                df = fetch_df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
        else:
            df = fetch_df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
        # if able to merge fetch + last for today
    elif (
            use_fetch_name == 'tdputs' or
            fetch_type == td_consts.FETCH_TD_PUTS):
        status_df, fetch_df = td_fetch.fetch_puts(
            work_dict=work_dict)
        if status_df == ae_consts.SUCCESS:
            log.info(
                'put - merge df')
            work_copy = copy.deepcopy(
                work_dict)
            work_copy['ft_type'] = td_consts.FETCH_TD_PUTS
            work_copy['fd_type'] = 'tdputs'
            if 'tdputs' in work_dict:
                work_copy['redis_key'] = work_dict['tdputs']
                work_copy['s3_key'] = '{}.json'.format(
                    work_dict['tdputs'])
            else:
                work_copy['redis_key'] = (
                    '{}_tdputs'.format(
                        work_dict['redis_key']))
                work_copy['s3_key'] = (
                    '{}_tdputs'.format(
                        work_dict['s3_key']))
            ext_status, ext_df = \
                td_extract.extract_option_puts_dataset(
                    work_dict=work_copy)
            if ext_status == ae_consts.SUCCESS and len(ext_df.index) > 0:
                log.info(
                    'put - merging fetch={} with ext={}'.format(
                        len(fetch_df.index),
                        len(ext_df.index)))
                """
                for testing compression:
                """
                """
                import sys
                print(ext_df['date'])
                sys.exit(1)
                """
                extracted_records = json.loads(ext_df.to_json(
                    orient='records'))
                fetched_records = json.loads(fetch_df.to_json(
                    orient='records'))
                new_records = []
                dates_by_strike_dict = {}
                for ex_row in extracted_records:
                    date_strike_name = (
                        '{}_{}'.format(
                            ex_row['created'],
                            ex_row['strike']))
                    if date_strike_name not in dates_by_strike_dict:
                        new_node = {}
                        for c in td_consts.TD_OPTION_COLUMNS:
                            if c in ex_row:
                                new_node[c] = ex_row[c]
                        # end of for all columns to copy over
                        new_node.pop('index', None)
                        new_node.pop('level_0', None)
                        new_records.append(new_node)
                        dates_by_strike_dict[date_strike_name] = True
                # build extracted records

                for ft_row in fetched_records:
                    date_strike_name = (
                        '{}_{}'.format(
                            ft_row['created'],
                            ft_row['strike']))
                    try:
                        if date_strike_name not in dates_by_strike_dict:
                            new_node = {}
                            for c in td_consts.TD_OPTION_COLUMNS:
                                if c in ft_row:
                                    new_node[c] = ft_row[c]
                            # end of for all columns to copy over
                            new_node.pop('index', None)
                            new_node.pop('level_0', None)
                            new_records.append(new_node)
                            dates_by_strike_dict[date_strike_name] = True
                        else:
                            log.error(
                                'already have {} put - date={} '
                                'strike={}'.format(
                                    ticker,
                                    ft_row['created'],
                                    ft_row['strike']))
                    except Exception as p:
                        log.critical(
                            'failed fetching puts with ex={}'.format(
                                p))
                        return ae_consts.ERR, None
                # end of adding fetched records after the extracted

                df = pd.DataFrame(new_records)
                df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
                log.info(
                    'put - merged={}'.format(
                        len(df.index)))
            else:
                df = fetch_df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
        else:
            df = fetch_df.sort_values(
                    by=[
                        'date',
                        'strike'
                    ],
                    ascending=True)
        # if able to merge fetch + last for today
    else:
        log.error(
            'label={} - unsupported fetch_data('
            'work_dict={}, '
            'fetch_type={}'
            ')'.format(
                work_dict.get('label', None),
                work_dict,
                fetch_type))
        raise NotImplemented
    # end of supported fetchers

    return status_df, df
# end of fetch_data
