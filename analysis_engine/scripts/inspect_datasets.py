#!/usr/bin/env python

"""
Tool for inspecting cached pricing data to find common errors.
This tool uses the
`Extraction API <https://stock-analysis-engine.
readthedocs.io/en/latest/extract.html>`__ to look for dates
that are not in sync with the redis cached date.

.. note:: This tool requires redis to be running with
    fetched datasets already stored in supported
    keys

**Examples**

**Inspect Minute Datasets for a Ticker**

::

    inspect_datasets.py -t SPY

**Inspect Daily Datasets for a Ticker**

::

    inspect_datasets.py -t AAPL -g daily
    # or
    # inspect_datasets.py -t AAPL -g day

**Usage**

::

    inspect_datasets.py -h
    usage: inspect_datasets.py [-h] [-t TICKER] [-g DATASETS] [-s START_DATE]

    Inspect datasets looking for dates in redis that look incorrect

    optional arguments:
    -h, --help     show this help message and exit
    -t TICKER      ticker
    -g DATASETS    optional - datasets: minute or min = examine IEX Cloud
                    intraday minute data, daily or day = examine IEX Cloud
                    daily
                    data, quote = examine IEX Cloud quotes data, stats =
                    examine
                    IEX Cloud key stats data, peers = examine IEX Cloud
                    peers
                    data, news = examine IEX Cloud news data, fin = examine
                    IEX
                    Cloud financials data, earn = examine IEX Cloud earnings
                    data, div = examine IEX Cloud dividendsdata, comp =
                    examine
                    IEX Cloud company data, calls = examine Tradier calls
                    data,
                    puts = examine Tradier puts data, and comma delimited is
                    supported as well
    -s START_DATE  start date format YYYY-MM-DD (default is 2019-01-01)
"""

import datetime
import argparse
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.extract as ae_extract
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(
    name='inspect-redis-data',
    handler_name='no_date_colors')


def inspect_datasets(
        ticker=None,
        start_date=None,
        datasets=None):
    """inspect_datasets

    Loop over all cached data in redis by going sequentially per date
    and examine the latest ``date`` value in the cache to
    check if it matches the redis key's date.

    For IEX Cloud minute data errors, running this function will print out
    commands to fix any issues (if possible):

    ::

        fetch -t TICKER -g iex_min -F DATE_TO_FIX

    :param ticker: optional - string ticker
    :param start_date: optional - datetime
        start date for the loop
        (default is ``2019-01-01``)
    :param datasets: optional - list of strings
        to extract specific, supported datasets
        (default is ``['minute']``)
    """

    if not start_date:
        start_date = datetime.datetime(
            year=2019,
            month=1,
            day=1)
    if not datasets:
        datasets = [
            'minute'
        ]
    if not ticker:
        ticker = 'SPY'

    tickers = [
        ticker
    ]

    fix_suggestions = []
    last_close = ae_utils.last_close()
    for ticker in tickers:

        not_done = True
        cur_date = start_date
        while not_done:
            cur_date_str = cur_date.strftime(ae_consts.COMMON_DATE_FORMAT)

            log.info(
                f'extracting {ticker} date={cur_date_str}')

            res = None

            # get from a date or the latest if not set
            if cur_date_str:
                res = ae_extract.extract(
                    ticker=ticker,
                    date=cur_date_str,
                    datasets=datasets)
            else:
                res = ae_extract.extract(
                    ticker=ticker,
                    datasets=datasets)

            weekday_name = cur_date.strftime('%A')

            for ds_name in datasets:
                df = res[ticker][ds_name]

                if ae_consts.is_df(df=df):
                    if 'date' in df:
                        latest_date = df['date'].iloc[-1]
                        latest_date_str = latest_date.strftime(
                            ae_consts.COMMON_DATE_FORMAT)
                        if latest_date_str == cur_date_str:
                            log.info(
                                f'valid - {ds_name} latest dates match '
                                f'{weekday_name}: '
                                f'{latest_date_str} == {cur_date_str}')
                        else:
                            if ds_name != 'daily':
                                log.critical(
                                    f'{ds_name} latest dates does '
                                    f'NOT match on '
                                    f'{weekday_name} {cur_date_str} found: '
                                    f'{latest_date_str}')
                            else:
                                one_day_back = (
                                    latest_date + datetime.timedelta(days=1))
                                if weekday_name == 'Monday':
                                    one_day_back = (
                                        latest_date + datetime.timedelta(
                                            days=3))
                                latest_date_str = one_day_back.strftime(
                                    ae_consts.COMMON_DATE_FORMAT)
                                if latest_date_str == cur_date_str:
                                    log.info(
                                        f'valid - {ds_name} latest dates '
                                        f'match '
                                        f'{weekday_name}: '
                                        f'{latest_date_str} == '
                                        f'{cur_date_str}')
                                else:
                                    log.critical(
                                        f'{ds_name} latest dates does '
                                        f'NOT match on '
                                        f'{weekday_name} {cur_date_str} '
                                        f'found: '
                                        f'{latest_date_str}')

                            if ds_name == 'minute':
                                fix_suggestions.append(
                                    f'fetch -t {ticker} -g iex_min '
                                    f'-F {cur_date_str}')
                    else:
                        log.error(
                            f'{ds_name} df does not have a date column '
                            f'on {cur_date_str}')
                else:
                    log.error(
                        f'Missing {ds_name} df on {cur_date_str}')
            # end of inspecting datasets

            if cur_date > last_close:
                not_done = False
            else:
                cur_date += datetime.timedelta(days=1)
                not_a_weekday = True
                while not_a_weekday:
                    weekday = cur_date.date().weekday()
                    if weekday > 4:
                        log.debug(
                            'SKIP weekend day: '
                            f'{cur_date.strftime("%A on %Y-%m-%d")}')
                        cur_date += datetime.timedelta(days=1)
                    else:
                        not_a_weekday = False
        # end for all dates
    # end of for all tickers

    if len(fix_suggestions) > 0:
        print('-------------------------------')
        print(
            'Detected invalid dates - below are the suggested fixes '
            'to run using the fetch command.')
        print(
            ' - Please be aware fetching data may incur usages and '
            'costs on your account')
        for s in fix_suggestions:
            print(s)
    else:
        log.info(
            'done')
# end inspect_datasets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            'Inspect datasets looking for dates in redis '
            'that look incorrect'))
    parser.add_argument(
        '-t',
        help=(
            'ticker'),
        required=False,
        dest='ticker')
    parser.add_argument(
        '-g',
        help=(
            'optional - datasets: '
            'minute or min = examine IEX Cloud intraday minute data, '
            'daily or day  = examine IEX Cloud daily data, '
            'quote = examine IEX Cloud quotes data, '
            'stats = examine IEX Cloud key stats data, '
            'peers = examine IEX Cloud peers data, '
            'news = examine IEX Cloud news data, '
            'fin = examine IEX Cloud financials data, '
            'earn = examine IEX Cloud earnings data, '
            'div = examine IEX Cloud dividendsdata, '
            'comp = examine IEX Cloud company data, '
            'calls = examine Tradier calls data, '
            'puts = examine Tradier puts data, '
            'and comma delimited is supported as well'),
        required=False,
        dest='datasets')
    parser.add_argument(
        '-s',
        help=(
            'start date format YYYY-MM-DD (default is 2019-01-01)'),
        required=False,
        dest='start_date')
    args = parser.parse_args()

    start_date = datetime.datetime(
        year=2019,
        month=1,
        day=1)
    datasets = [
        'minute'
    ]
    ticker = 'SPY'

    valid = True
    if args.ticker:
        ticker = args.ticker.upper()
    if args.datasets:
        datasets = []
        for key in args.datasets.lower().split(','):
            if key == 'news':
                datasets.append('news1')
            elif key == 'min':
                datasets.append('minute')
            elif key == 'day':
                datasets.append('daily')
            elif key == 'fin':
                datasets.append('financials')
            elif key == 'earn':
                datasets.append('earnings')
            elif key == 'div':
                datasets.append('dividends')
            elif key == 'comp':
                datasets.append('company')
            elif key == 'calls':
                datasets.append('tdcalls')
            elif key == 'puts':
                datasets.append('tdputs')
            else:
                if key not in ae_consts.BACKUP_DATASETS:
                    log.error(
                        f'unsupported dataset key: {key} '
                        'please use a supported key: '
                        f'{ae_consts.BACKUP_DATASETS}')
                    valid = False
                else:
                    datasets.append(key)
    if args.start_date:
        start_date = datetime.datetime.strptime(
            args.start_date,
            '%Y-%m-%d')

    if valid:
        inspect_datasets(
            ticker=ticker,
            start_date=start_date,
            datasets=datasets)
