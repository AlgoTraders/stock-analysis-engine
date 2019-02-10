"""
Perform dataset scrubbing actions
and return the scrubbed dataset as a ready-to-go
data feed. This is an approach for normalizing
an internal data feed.

Supported environment variables:

::

    # verbose logging in this module
    # note this can take longer to transform
    # DataFrames and is not recommended for
    # production:
    export DEBUG_FETCH=1

Ingress Scrubbing supports converting an incoming
dataset (from IEX) and converts it to one
of the following data feed and returned as a
``pandas DataFrame``:

.. code-block:: python

    DATAFEED_DAILY = 900
    DATAFEED_MINUTE = 901
    DATAFEED_QUOTE = 902
    DATAFEED_STATS = 903
    DATAFEED_PEERS = 904
    DATAFEED_NEWS = 905
    DATAFEED_FINANCIALS = 906
    DATAFEED_EARNINGS = 907
    DATAFEED_DIVIDENDS = 908
    DATAFEED_COMPANY = 909
    DATAFEED_PRICING_YAHOO = 1100
    DATAFEED_OPTIONS_YAHOO = 1101
    DATAFEED_NEWS_YAHOO = 1102

"""

import datetime
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.iex.consts as iex_consts
import analysis_engine.yahoo.consts as yahoo_consts
import analysis_engine.td.consts as td_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def debug_msg(
        label,
        datafeed_type,
        msg_format,
        date_str,
        df):
    """debug_msg

    Debug helper for debugging scrubbing handlers

    :param label: log label
    :param datafeed_type: fetch type
    :param msg_format: message to include
    :param date_str: date string
    :param df: ``pandas DataFrame`` or ``None``
    """

    msg = msg_format.format('_', date_str)

    dft_msg = ''
    if (
            datafeed_type == yahoo_consts.DATAFEED_PRICING_YAHOO or
            datafeed_type == yahoo_consts.DATAFEED_OPTIONS_YAHOO or
            datafeed_type == yahoo_consts.DATAFEED_NEWS_YAHOO):
        dft_msg = yahoo_consts.get_datafeed_str_yahoo(
            df_type=datafeed_type)
    elif (
            datafeed_type == td_consts.DATAFEED_TD_CALLS or
            datafeed_type == td_consts.DATAFEED_TD_PUTS):
        dft_msg = td_consts.get_datafeed_str_td(
            df_type=datafeed_type)
    else:
        dft_msg = iex_consts.get_datafeed_str(
            df_type=datafeed_type)

    if ae_consts.ev('DEBUG_FETCH', '0') == '1':
        if 'START' in msg:
            log.info(
                f'{label} - {dft_msg} '
                f'-------------------------'
                f'------------------------------------')
        msg = msg_format.format(
            df,
            date_str),
        if hasattr(df, 'empty'):
            log.info(
                f'{label} - {dft_msg} - {msg} found df={df} '
                f'columns={df.columns.values}')
        else:
            log.info(
                f'{label} - {dft_msg} - {msg} found df={df}')

        if 'END' in msg:
            log.info(
                f'{label} - {dft_msg} '
                f'-------------------------'
                f'------------------------------------')
    else:
        log.info(
            f'{label} - {dft_msg} - {msg}')
    # end of debug pre-scrub logging

# end of debug_msg


def build_dates_from_df_col(
        df,
        use_date_str,
        src_col='minute',
        src_date_format=ae_consts.COMMON_TICK_DATE_FORMAT,
        output_date_format=ae_consts.COMMON_TICK_DATE_FORMAT):
    """build_dates_from_df_col

    Converts a string date column series in a ``pandas.DataFrame``
    to a well-formed date string list.

    :param src_col: source column name
    :param use_date_str: date string for today
    :param src_date_format: format of the string in the
                            ```df[src_col]`` columne
    :param output_date_format: write the new date strings
                               in this format.
    :param df: source ``pandas.DataFrame``
    """
    new_dates = []
    for idx, i in enumerate(df[src_col]):
        org_new_str = ''
        if ':' not in i:
            split_arr = i.split(' ')
            org_new_str = (
                f'{use_date_str} '
                f'{split_arr[0]}'
                f':00:00 '
                f'{split_arr[1]}')
        else:
            org_new_str = (
                f'{use_date_str} '
                f'{i}:00')
        new_date_val = datetime.datetime.strptime(
            org_new_str,
            src_date_format)
        new_str = new_date_val.strftime(
            output_date_format)
        new_dates.append(new_str)
    # for all rows

    return new_dates
# end of build_dates_from_df_col


def ingress_scrub_dataset(
        label,
        datafeed_type,
        df,
        date_str=None,
        msg_format=None,
        scrub_mode='sort-by-date',
        ds_id='no-id'):
    """ingress_scrub_dataset

    Scrub a ``pandas.DataFrame`` from an Ingress pricing service
    and return the resulting ``pandas.DataFrame``

    :param label: log label
    :param datafeed_type: ``analysis_engine.iex.consts.DATAFEED_*`` type
        or ``analysis_engine.yahoo.consts.DATAFEED_*```
        type
        .. code-block:: python

            DATAFEED_DAILY = 900
            DATAFEED_MINUTE = 901
            DATAFEED_QUOTE = 902
            DATAFEED_STATS = 903
            DATAFEED_PEERS = 904
            DATAFEED_NEWS = 905
            DATAFEED_FINANCIALS = 906
            DATAFEED_EARNINGS = 907
            DATAFEED_DIVIDENDS = 908
            DATAFEED_COMPANY = 909
            DATAFEED_PRICING_YAHOO = 1100
            DATAFEED_OPTIONS_YAHOO = 1101
            DATAFEED_NEWS_YAHOO = 1102

    :param df: ``pandas DataFrame``
    :param date_str: date string for simulating historical dates
                     or ``datetime.datetime.now()`` if not
                     set
    :param msg_format: msg format for a ``string.format()``
    :param scrub_mode: mode to scrub this dataset
    :param ds_id: dataset identifier
    """

    if not hasattr(df, 'empty'):
        log.debug(
            f'{label} - {datafeed_type} no dataset_id={ds_id}')
        return None

    out_df = df

    daily_date_format = '%I:%M %p'
    minute_date_format = '%I:%M %p'

    use_date_str = date_str
    last_close_date = ae_utils.last_close()
    today_str = last_close_date.strftime('%Y-%m-%d')

    year_str = today_str.split('-')[0]
    if not use_date_str:
        use_date_str = today_str

    daily_date_format = ae_consts.IEX_DAILY_DATE_FORMAT
    minute_date_format = ae_consts.IEX_MINUTE_DATE_FORMAT

    """
    use_msg_format = msg_format
    if not msg_format:
        use_msg_format = 'df={} date_str={}'

    debug_msg(
        label=label,
        datafeed_type=datafeed_type,
        msg_format=f'START - {use_msg_format}',
        date_str=use_date_str,
        df=df)
    """

    try:
        if scrub_mode == 'sort-by-date':
            if datafeed_type == iex_consts.DATAFEED_DAILY:
                new_dates = []
                if 'label' in df:
                    for idx, i in enumerate(out_df['label']):
                        split_arr = i.split(' ')
                        new_str = ''
                        if ',' not in i:
                            # Oct 3
                            new_str = (
                                f'{year_str}-{split_arr[0]}-{split_arr[1]}')
                        else:
                            # Aug 29, 18
                            new_str = (
                                f'20{split_arr[2]}-{split_arr[0]}-'
                                f'{split_arr[1].replace(",", "")}')
                        new_dates.append(new_str)
                    # end for all rows
                    out_df['date'] = pd.to_datetime(
                        new_dates,
                        format=daily_date_format)
                # end if label is in df
            elif datafeed_type == iex_consts.DATAFEED_MINUTE:
                new_dates = []
                if 'label' in df:
                    new_dates = build_dates_from_df_col(
                        src_col='label',
                        src_date_format=minute_date_format,
                        use_date_str=use_date_str,
                        df=out_df)
                    out_df['date'] = pd.to_datetime(
                        new_dates,
                        format='%Y-%m-%d %H:%M:%S')
                # end if label is in df
            elif datafeed_type == iex_consts.DATAFEED_QUOTE:
                columns_list = out_df.columns.values
                if 'latestTime' in columns_list:
                    out_df['date'] = pd.to_datetime(
                        out_df['latestTime'],
                        format=ae_consts.IEX_QUOTE_DATE_FORMAT)
                if 'latestUpdate' in columns_list:
                    out_df['latest_update'] = pd.to_datetime(
                        out_df['latestUpdate'],
                        unit='ns')
                if 'extendedPriceTime' in columns_list:
                    out_df['extended_price_time'] = pd.to_datetime(
                        out_df['extendedPriceTime'],
                        unit='ns')
                if 'iexLastUpdated' in columns_list:
                    out_df['iex_last_update'] = pd.to_datetime(
                        out_df['iexLastUpdated'],
                        unit='ns')
                if 'openTime' in columns_list:
                    out_df['open_time'] = pd.to_datetime(
                        out_df['openTime'],
                        unit='ns')
                if 'closeTime' in columns_list:
                    out_df['close_time'] = pd.to_datetime(
                        out_df['closeTime'],
                        unit='ns')
                # end if label is in df
            elif datafeed_type == iex_consts.DATAFEED_STATS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_PEERS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_NEWS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_FINANCIALS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_EARNINGS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_DIVIDENDS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == iex_consts.DATAFEED_COMPANY:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == yahoo_consts.DATAFEED_PRICING_YAHOO:
                if 'date' in df:
                    out_df['date'] = pd.to_datetime(
                        df['date'],
                        format=daily_date_format)
            elif datafeed_type == yahoo_consts.DATAFEED_OPTIONS_YAHOO:
                if 'date' in df:
                    out_df['date'] = pd.to_datetime(
                        df['date'],
                        format=daily_date_format)
            elif datafeed_type == yahoo_consts.DATAFEED_NEWS_YAHOO:
                if 'date' in df:
                    out_df['date'] = pd.to_datetime(
                        df['date'],
                        format=daily_date_format)
            elif datafeed_type == td_consts.DATAFEED_TD_CALLS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            elif datafeed_type == td_consts.DATAFEED_TD_PUTS:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            else:
                log.debug('{label} - {datafeed_type} - no scrub_mode')
            # if/else
        else:
            log.debug(
                f'{label} - {datafeed_type} - '
                f'missing support in ingress_scrub_dataset')
    except Exception as e:
        log.critical(
            f'{label} - {datafeed_type} sort={scrub_mode} - '
            f'failed with ex={e} data={df}')
        out_df = None
    # end of try/ex

    """
    debug_msg(
        label=label,
        datafeed_type=datafeed_type,
        msg_format='END - df={} date_str={}',
        date_str=use_date_str,
        df=out_df)
    """

    return out_df
# end of ingress_scrub_dataset


def extract_scrub_dataset(
        label,
        datafeed_type,
        df,
        date_str=None,
        msg_format=None,
        scrub_mode='sort-by-date',
        ds_id='no-id'):
    """extract_scrub_dataset

    Scrub a cached ``pandas.DataFrame`` that was stored
    in Redis and return the resulting ``pandas.DataFrame``

    :param label: log label
    :param datafeed_type: ``analysis_engine.iex.consts.DATAFEED_*`` type
        or ``analysis_engine.yahoo.consts.DATAFEED_*```
        type
        .. code-block:: python

            DATAFEED_DAILY = 900
            DATAFEED_MINUTE = 901
            DATAFEED_QUOTE = 902
            DATAFEED_STATS = 903
            DATAFEED_PEERS = 904
            DATAFEED_NEWS = 905
            DATAFEED_FINANCIALS = 906
            DATAFEED_EARNINGS = 907
            DATAFEED_DIVIDENDS = 908
            DATAFEED_COMPANY = 909
            DATAFEED_PRICING_YAHOO = 1100
            DATAFEED_OPTIONS_YAHOO = 1101
            DATAFEED_NEWS_YAHOO = 1102
    :param df: ``pandas DataFrame``
    :param date_str: date string for simulating historical dates
                     or ``datetime.datetime.now()`` if not
                     set
    :param msg_format: msg format for a ``string.format()``
    :param scrub_mode: mode to scrub this dataset
    :param ds_id: dataset identifier
    """

    if not hasattr(df, 'empty'):
        log.info(
            f'{label} - {datafeed_type} no dataset_id={ds_id}')
        return None

    return df
# end of extract_scrub_dataset
