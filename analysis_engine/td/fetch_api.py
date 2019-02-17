"""
Fetch API calls wrapping Tradier

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_FETCH=1

"""

import json
import datetime
import requests
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.options_dates as opt_dates
import analysis_engine.url_helper as url_helper
import analysis_engine.dataset_scrub_utils as scrub_utils
import analysis_engine.td.consts as td_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def fetch_calls(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_calls

    Fetch Tradier option calls for a ticker and
    return a tuple: (status, ``pandas.DataFrame``)

    .. code-block:: python

        import analysis_engine.td.fetch_api as td_fetch

        # Please set the TD_TOKEN environment variable to your token
        calls_status, calls_df = td_fetch.fetch_calls(
            ticker='SPY')

        print(f'Fetched SPY Option Calls from Tradier status={calls_status}:')
        print(calls_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string type of
        scrubbing handler to run
    :param verbose: optional - bool for debugging
    """
    label = 'fetch_calls'
    datafeed_type = td_consts.DATAFEED_TD_CALLS
    exp_date = None
    latest_pricing = {}
    latest_close = None

    if work_dict:
        ticker = work_dict.get(
            'ticker',
            ticker)
        label = work_dict.get(
            'label',
            label)
        exp_date = work_dict.get(
            'exp_date',
            exp_date)
        latest_pricing = work_dict.get(
            'latest_pricing',
            latest_pricing)
        latest_close = latest_pricing.get(
            'close',
            latest_close)

    log.debug(
        f'{label} - calls - close={latest_close} '
        f'ticker={ticker}')

    exp_date = opt_dates.option_expiration().strftime(
        ae_consts.COMMON_DATE_FORMAT)
    use_url = td_consts.TD_URLS['options'].format(
        ticker,
        exp_date)
    headers = td_consts.get_auth_headers()
    session = requests.Session()
    session.headers = headers
    res = url_helper.url_helper(sess=session).get(
        use_url
    )

    if res.status_code != requests.codes.OK:
        if res.status_code in [401, 403]:
            log.critical(
                'Please check the TD_TOKEN is correct '
                f'received {res.status_code} during '
                'fetch for: calls')
        else:
            log.info(
                f'failed to get call with response={res} '
                f'code={res.status_code} '
                f'text={res.text}')
        return ae_consts.EMPTY, pd.DataFrame([{}])
    records = json.loads(res.text)
    org_records = records.get(
        'options', {}).get(
            'option', [])

    if len(org_records) == 0:
        log.info(
            'failed to get call records '
            'text={}'.format(
                res.text))
        return ae_consts.EMPTY, pd.DataFrame([{}])

    options_list = []

    # assumes UTC conversion will work with the system clock
    created_minute = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime(
            '%Y-%m-%d %H:%M:00')
    last_close_date = ae_utils.get_last_close_str(
        fmt='%Y-%m-%d %H:%M:00')

    # hit bug where dates were None
    if not last_close_date:
        last_close_date = created_minute

    for node in org_records:
        node['date'] = last_close_date
        node['created'] = created_minute
        node['ticker'] = ticker
        if (
                node['option_type'] == 'call' and
                node['expiration_type'] == 'standard' and
                float(node['bid']) > 0.01):
            node['opt_type'] = int(ae_consts.OPTION_CALL)
            node['exp_date'] = node['expiration_date']

            new_node = {}
            for col in td_consts.TD_OPTION_COLUMNS:
                if col in node:
                    if col in td_consts.TD_EPOCH_COLUMNS:
                        # trade_date can be None
                        if node[col] == 0:
                            new_node[col] = None
                        else:
                            new_node[col] = ae_utils.epoch_to_dt(
                                epoch=node[col]/1000,
                                use_utc=False,
                                convert_to_est=True).strftime(
                                    ae_consts.COMMON_TICK_DATE_FORMAT)
                            """
                            Debug epoch ms converter:
                            """
                            """
                            print('-----------')
                            print(col)
                            print(node[col])
                            print(new_node[col])
                            print('===========')
                            """
                        # if/else valid date
                    else:
                        new_node[col] = node[col]
                    # if date column to convert
                # if column is in the row
            # convert all columns

            options_list.append(new_node)
    # end of records

    full_df = pd.DataFrame(options_list).sort_values(
        by=[
            'strike'
        ],
        ascending=True)

    num_chains = len(full_df.index)

    df = None
    if latest_close:
        df_filter = (
            (full_df['strike'] >=
                (latest_close - ae_consts.OPTIONS_LOWER_STRIKE)) &
            (full_df['strike'] <=
                (latest_close + ae_consts.OPTIONS_UPPER_STRIKE)))
        df = full_df[df_filter].copy().sort_values(
            by=[
                'date',
                'strike'
            ]).reset_index()
    else:
        mid_chain_idx = int(num_chains / 2)
        low_idx = int(
            mid_chain_idx - ae_consts.MAX_OPTIONS_LOWER_STRIKE)
        high_idx = int(
            mid_chain_idx + ae_consts.MAX_OPTIONS_UPPER_STRIKE)
        if low_idx < 0:
            low_idx = 0
        if high_idx > num_chains:
            high_idx = num_chains
        df = full_df[low_idx:high_idx].copy().sort_values(
            by=[
                'date',
                'strike'
            ]).reset_index()

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=exp_date,
        df=df)

    return ae_consts.SUCCESS, scrubbed_df
# end of fetch_calls


def fetch_puts(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_puts

    Fetch Tradier option puts for a ticker and
    return a tuple: (status, ``pandas.DataFrame``)

    .. code-block:: python

        import analysis_engine.td.fetch_api as td_fetch

        puts_status, puts_df = td_fetch.fetch_puts(
            ticker='SPY')

        print(f'Fetched SPY Option Puts from Tradier status={puts_status}:')
        print(puts_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string type of
        scrubbing handler to run
    :param verbose: optional - bool for debugging
    """
    label = 'fetch_calls'
    datafeed_type = td_consts.DATAFEED_TD_PUTS
    exp_date = None
    latest_pricing = {}
    latest_close = None

    if work_dict:
        ticker = work_dict.get(
            'ticker',
            ticker)
        label = work_dict.get(
            'label',
            label)
        exp_date = work_dict.get(
            'exp_date',
            exp_date)
        latest_pricing = work_dict.get(
            'latest_pricing',
            latest_pricing)
        latest_close = latest_pricing.get(
            'close',
            latest_close)

    if verbose:
        log.info(
            f'{label} - puts - close={latest_close} '
            f'ticker={ticker}')

    exp_date = opt_dates.option_expiration().strftime(
        ae_consts.COMMON_DATE_FORMAT)
    use_url = td_consts.TD_URLS['options'].format(
        ticker,
        exp_date)
    headers = td_consts.get_auth_headers()
    session = requests.Session()
    session.headers = headers
    res = url_helper.url_helper(sess=session).get(
        use_url
    )

    if res.status_code != requests.codes.OK:
        if res.status_code in [401, 403]:
            log.critical(
                'Please check the TD_TOKEN is correct '
                f'received {res.status_code} during '
                'fetch for: puts')
        else:
            log.info(
                f'failed to get put with response={res} '
                f'code={res.status_code} '
                f'text={res.text}')
        return ae_consts.EMPTY, pd.DataFrame([{}])
    records = json.loads(res.text)
    org_records = records.get(
        'options', {}).get(
            'option', [])

    if len(org_records) == 0:
        log.info(
            'failed to get put records '
            'text={}'.format(
                res.text))
        return ae_consts.EMPTY, pd.DataFrame([{}])

    options_list = []

    # assumes UTC conversion will work with the system clock
    created_minute = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime(
            '%Y-%m-%d %H:%M:00')
    last_close_date = ae_utils.get_last_close_str(
        fmt='%Y-%m-%d %H:%M:00')

    # hit bug where dates were None
    if not last_close_date:
        last_close_date = created_minute

    for node in org_records:
        node['date'] = last_close_date
        node['created'] = created_minute
        node['ticker'] = ticker
        if (
                node['option_type'] == 'put' and
                node['expiration_type'] == 'standard' and
                float(node['bid']) > 0.01):
            node['opt_type'] = int(ae_consts.OPTION_PUT)
            node['exp_date'] = node['expiration_date']

            new_node = {}
            for col in td_consts.TD_OPTION_COLUMNS:
                if col in node:
                    if col in td_consts.TD_EPOCH_COLUMNS:
                        # trade_date can be None
                        if node[col] == 0:
                            new_node[col] = None
                        else:
                            new_node[col] = ae_utils.epoch_to_dt(
                                epoch=node[col]/1000,
                                use_utc=False,
                                convert_to_est=True).strftime(
                                    ae_consts.COMMON_TICK_DATE_FORMAT)
                            """
                            Debug epoch ms converter:
                            """
                            """
                            print('-----------')
                            print(col)
                            print(node[col])
                            print(new_node[col])
                            print('===========')
                            """
                        # if/else valid date
                    else:
                        new_node[col] = node[col]
                    # if date column to convert
                # if column is in the row
            # convert all columns

            options_list.append(new_node)
    # end of records

    full_df = pd.DataFrame(options_list).sort_values(
        by=[
            'strike'
        ],
        ascending=True)

    num_chains = len(full_df.index)

    df = None
    if latest_close:
        df_filter = (
            (full_df['strike'] >=
                (latest_close - ae_consts.OPTIONS_LOWER_STRIKE)) &
            (full_df['strike'] <=
                (latest_close + ae_consts.OPTIONS_UPPER_STRIKE)))
        df = full_df[df_filter].copy().sort_values(
            by=[
                'date',
                'strike'
            ]).reset_index()
    else:
        mid_chain_idx = int(num_chains / 2)
        low_idx = int(
            mid_chain_idx - ae_consts.MAX_OPTIONS_LOWER_STRIKE)
        high_idx = int(
            mid_chain_idx + ae_consts.MAX_OPTIONS_UPPER_STRIKE)
        if low_idx < 0:
            low_idx = 0
        if high_idx > num_chains:
            high_idx = num_chains
        df = full_df[low_idx:high_idx].copy().sort_values(
            by=[
                'date',
                'strike'
            ]).reset_index()

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=exp_date,
        df=df)

    return ae_consts.SUCCESS, scrubbed_df
# end of fetch_puts
