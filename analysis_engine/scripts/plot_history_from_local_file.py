#!/usr/bin/env python

"""
A tool for plotting an algorithm's ``Trading History`` from
a locally saved file from running the backtester with
the save to file option enabled:

::

    run_backtest_and_plot_history.py -t SPY -f <SAVE_HISTORY_TO_THIS_FILE>
"""

import os
import argparse
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.plot_trading_history as plot_trading_history
import spylunking.log.setup_logging as log_utils


log = log_utils.build_colorized_logger(
    name='plot-history',
    log_config_path=ae_consts.LOG_CONFIG_PATH)


def plot_local_history_file():
    """plot_local_history_file

    Run a derived algorithm with an algorithm config dictionary

    :param config_dict: algorithm config dictionary
    """

    log.debug('start - plot')

    parser = argparse.ArgumentParser(
        description=(
            'plot a local algorithm trading history file'))
    parser.add_argument(
        '-f',
        help=(
            'plot this trading history dataframe '
            'saved in this file'),
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

    history_json_file = None
    debug = False

    if args.history_json_file:
        history_json_file = args.history_json_file
    if args.debug:
        debug = True

    if not history_json_file:
        log.error(
            'usage error - please run with: '
            '-f <path to local trading history file>')
        return
    elif not os.path.exists(history_json_file):
        log.error(
            'did not find trading history file={}'.format(
                history_json_file))
        return
    # end of checking the file arg is set and exists on disk

    log.info(
        'plotting history to: {}'.format(
            history_json_file))
    history_df = pd.read_json(
        history_json_file,
        orient='records')

    history_df['date'] = pd.to_datetime(
        history_df['date'])
    history_df['minute'] = pd.to_datetime(
        history_df['minute'])
    ticker = history_df['ticker'].iloc[0]

    log.info('plotting history')

    first_date = history_df['date'].iloc[0]
    end_date = history_df['date'].iloc[-1]
    title = (
        'Trading History {}\n'
        'Backtest dates from {} to {}'.format(
            ticker,
            first_date,
            end_date))
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
            log.info('{} - {}'.format(
                r['minute'],
                r['close']))
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

# end of plot_local_history_file


if __name__ == '__main__':
    plot_local_history_file()
