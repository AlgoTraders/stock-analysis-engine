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
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_calls

    Fetch the Tradier calls data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return fetch('call', work_dict, scrub_mode=scrub_mode)
# end of fetch_calls


def fetch_puts(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_puts

    Fetch the Tradier puts intraday data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return fetch('put', work_dict, scrub_mode=scrub_mode)
# end of fetch_puts


def fetch(
        fetch_type,
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch

    Fetch the Tradier calls/puts data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param fetch_type: fetch type of either 'call' or 'put'
    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    if not fetch_type or fetch_type not in ['call', 'put']:
        return ae_consts.NOT_RUN
    is_put = bool(fetch_type == 'put')
    datafeed_type = (
        td_consts.DATAFEED_TD_PUTS if is_put else td_consts.DATAFEED_TD_CALLS)
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    exp_date = work_dict.get(
        'exp_date',
        None)

    log.debug(
        f'{label} - {fetch_type} - scrub_mode={scrub_mode} '
        f'args={work_dict} ticker={ticker}')

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
                f'fetch for: {fetch_type}s')
        else:
            log.info(
                f'failed to get {fetch_type} with response={res} '
                f'code={res.status_code} '
                f'text={res.text}')
        return ae_consts.EMPTY, pd.DataFrame([{}])
    records = json.loads(res.text)
    org_records = records.get(
        'options', {}).get(
            'option', [])

    if len(org_records) == 0:
        log.info(
            f'failed to get {fetch_type} records '
            f'text={res.text}')
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
                node['option_type'] == fetch_type and
                node['expiration_type'] == 'standard'):
            node['opt_type'] = int(
                ae_consts.OPTION_PUT if is_put else ae_consts.OPTION_CALL)
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
    mid_chain_idx = int(num_chains / 2)
    low_idx = int(
        mid_chain_idx - (30 if is_put else 20))
    high_idx = int(
        mid_chain_idx + (20 if is_put else 30))
    if low_idx < 0:
        low_idx = 0
    if high_idx > num_chains:
        high_idx = num_chains

    df = full_df[low_idx:high_idx].copy().sort_values(by=[
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
# end of fetch
