#!/usr/bin/env python

"""
Algorithm Runner API Example Script

**Run Full Backtest**

::

    backtest_with_runner.py -t TICKER -b S3_BUCKET -k S3_KEY -c ALGO_CONFIG

**Run Algorithm with Latest Pricing Data**

::

    backtest_with_runner.py -l -t TICKER -b S3_BUCKET -k S3_KEY -c ALGO_CONFIG

Debug by adding ``-d`` as an argument
"""

import sys
import argparse
import analysis_engine.utils as ae_utils
import analysis_engine.algo_runner as algo_runner
import analysis_engine.plot_trading_history as plot
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(
    name='algo-runner')


def backtest_with_runner():
    """backtest_with_runner

    build and publish a trading history from an algorithm config.

    ::

        backtest_with_runner.py -t TICKER -c ALGO_CONFIG -s START_DATE
        -k S3_KEY -b S3_BUCKET -l
    """

    parser = argparse.ArgumentParser(
        description=(
            'backtest an algorithm and publish '
            'the trading history'))
    parser.add_argument(
        '-t',
        help=('ticker symbol'),
        required=False,
        dest='ticker')
    parser.add_argument(
        '-k',
        help=('s3_key'),
        required=False,
        dest='s3_key')
    parser.add_argument(
        '-b',
        help=('s3_bucket'),
        required=False,
        dest='s3_bucket')
    parser.add_argument(
        '-s',
        help=('start date format YYYY-MM-DD'),
        required=False,
        dest='start_date')
    parser.add_argument(
        '-c',
        help=('algo config file'),
        required=False,
        dest='algo_config')
    parser.add_argument(
        '-l',
        help=(
            'run a backtest with the latest '
            'pricing data'),
        required=False,
        dest='latest',
        action='store_true')
    parser.add_argument(
        '-d',
        help='debug',
        required=False,
        dest='debug',
        action='store_true')
    args = parser.parse_args()

    ticker = 'SPY'
    s3_bucket = (
        f'algohistory')
    s3_key = (
        f'trade_history_{ticker}')
    start_date = (
        f'2019-01-01')
    algo_config = (
        f'/opt/sa/cfg/default_algo.json')
    latest = False
    show_plot = True
    debug = False

    if args.ticker:
        ticker = args.ticker.upper()
    if args.s3_key:
        s3_key = args.s3_key
    if args.s3_bucket:
        s3_bucket = args.s3_bucket
    if args.start_date:
        start_date = args.start_date
    if args.algo_config:
        algo_config = args.algo_config
    if args.latest:
        latest = True
        start_date = ae_utils.get_last_close_str()
    if args.debug:
        debug = True

    history_loc = (
        f's3://{s3_bucket}/{s3_key}')

    log.info(
        f'building {ticker} trade history '
        f'start_date={start_date} '
        f'config={algo_config} '
        f'history_loc={history_loc}')

    runner = algo_runner.AlgoRunner(
        ticker=ticker,
        start_date=start_date,
        history_loc=history_loc,
        algo_config=algo_config,
        verbose_algo=debug,
        verbose_processor=False,
        verbose_indicators=False)

    trading_history_df = None
    if latest:
        trading_history_df = runner.latest()
        log.info(
            f'{ticker} latest:')
        print(trading_history_df[['minute', 'close']].tail(5))
        log.info(
            f'Other available columns to plot:')
        print(trading_history_df.columns.values)
        if show_plot:
            plot.plot_trading_history(
                title=(
                    f'{ticker} at '
                    f'${trading_history_df["close"].iloc[-1]} '
                    f'at: '
                    f'{trading_history_df["minute"].iloc[-1]}'),
                df=trading_history_df,
                red='high',
                blue='close')
    else:
        runner.start()

    sys.exit(0)
# end of backtest_with_runner


if __name__ == '__main__':
    backtest_with_runner()
