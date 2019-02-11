#!/usr/bin/env python

"""
A tool for plotting an algorithm's ``Trading History`` from
a file in s3 from running the backtester with
the save to file option enabled:

::

    run_backtest_and_plot_history.py -t SPY -f <SAVE_HISTORY_TO_THIS_FILE>
"""

import argparse
import pandas as pd
import analysis_engine.consts as consts
import analysis_engine.plot_trading_history as plot_trading_history
import analysis_engine.load_history_dataset as load_history
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name='view-history-in-s3')


def plot_history_from_s3():
    """plot_history_from_s3

    Run a derived algorithm with an algorithm config dictionary

    :param config_dict: algorithm config dictionary
    """

    log.debug('start - plot')

    parser = argparse.ArgumentParser(
        description=(
            'plot a local algorithm trading history file'))
    parser.add_argument(
        '-b',
        help=(
            'saved in this s3 bucket'),
        required=False,
        dest='s3_bucket')
    parser.add_argument(
        '-k',
        help=(
            'saved in this s3 key'),
        required=False,
        dest='history_json_file')
    parser.add_argument(
        '-d',
        help=(
            'debug'),
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    s3_access_key = consts.S3_ACCESS_KEY
    s3_secret_key = consts.S3_SECRET_KEY
    s3_region_name = consts.S3_REGION_NAME
    s3_address = consts.S3_ADDRESS
    s3_secure = consts.S3_SECURE
    compress = True

    s3_bucket = (
        'bt-spy-williamsr-2018-12-05-22-44-50-714400')
    s3_key = (
        '-181.55_netgain_9818.45_netvalue_NEGATIVE_'
        '10000.0_startbalance_1710.95_endbalance_'
        '30_shares_270.25_close_3_buys_0_sells_'
        '1_minbuyinds_1_minsellinds_'
        '43.52_seconds_'
        'trade_history-SPY_williamsr_test_'
        '0.73_for_176_of_24000.json')

    debug = False

    if args.debug:
        debug = True

    load_res = load_history.load_history_dataset(
        s3_enabled=True,
        s3_key=s3_key,
        s3_address=s3_address,
        s3_bucket=s3_bucket,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_region_name=s3_region_name,
        s3_secure=s3_secure,
        compress=compress)

    algo_config = load_res.get(
        'algo_config_dict',
        None)
    algo_name = load_res.get(
        'algo_name',
        None)
    tickers = load_res.get(
        'tickers',
        [
            'SPY',
        ])
    ticker = tickers[0]

    log.info(f'found algo: {algo_name}')
    log.info(f'config: {consts.ppj(algo_config)}')

    history_df = load_res[ticker]
    history_df['date'] = pd.to_datetime(
        history_df['date'])
    history_df['minute'] = pd.to_datetime(
        history_df['minute'])
    ticker = history_df['ticker'].iloc[0]

    log.info('plotting history')

    first_date = history_df['date'].iloc[0]
    end_date = history_df['date'].iloc[-1]
    title = (
        f'Trading History {ticker}\n'
        f'Backtest dates from {first_date} to {end_date}')
    use_xcol = 'date'
    use_as_date_format = '%d\n%b'
    use_minute = False
    if 'minute' in history_df:
        found_valid_minute = history_df['minute'].iloc[0]
        if found_valid_minute:
            use_minute = True

    if use_minute:
        use_xcol = 'minute'
        use_as_date_format = '%d %H:%M:%S\n%b'
    xlabel = 'Dates vs Algo values'
    ylabel = 'Algo values'
    df_filter = (history_df['close'] > 1.00)

    # set default hloc columns:
    blue = None
    green = None
    orange = None

    red = 'close'
    blue = 'balance'

    if debug:
        for i, r in history_df.iterrows():
            log.info(f'{r["minute"]} - {r["close"]}')
    # end of debug

    show_plot = True
    if show_plot:
        plot_trading_history.plot_trading_history(
            title=title,
            df=history_df,
            red=red,
            blue=blue,
            green=green,
            orange=orange,
            date_col=use_xcol,
            date_format=use_as_date_format,
            xlabel=xlabel,
            ylabel=ylabel,
            df_filter=df_filter,
            show_plot=True,
            dropna_for_all=True)

# end of plot_history_from_s3


if __name__ == '__main__':
    plot_history_from_s3()
