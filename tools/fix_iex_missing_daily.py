#!/usr/bin/env python

"""
Tool for fixing option dates that have 'date' == 0

.. note:: This tool requires redis to be running with
    fetched datasets already stored in supported
    keys
"""

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.extract as ae_extract
import analysis_engine.publish as ae_publish
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(
    name='fixer')


def fix_df(
        df):
    """fix_df

    :param df: ``pandas.DataFrame`` df
    """

    use_df = df

    new_recs = []

    cols = list(use_df.columns.values)
    num_to_copy = len(use_df.index) - 2
    for idx, row in use_df.iterrows():
        new_row = {}
        for c in cols:
            new_row[c] = row[c]
            if c == 'date':
                log.info(f' - including: {new_row[c]}')
        new_recs.append(new_row)
        if num_to_copy > 0:
            num_to_copy -= 1
        else:
            break

    fixed_df = pd.DataFrame(new_recs)

    if 'date' in fixed_df:
        fixed_df.sort_values(
                by=[
                    'date'
                ],
                ascending=True).reset_index()

    print(fixed_df)
    return fixed_df
# end of fix_df


use_redis_address = ae_consts.REDIS_ADDRESS
last_close_str = ae_utils.get_last_close_str(
    ae_consts.COMMON_DATE_FORMAT)
use_date_str = last_close_str

src_date = '2019-02-15'
dst_date = src_date
dst_date = '2019-02-14'
tickers = ['SPY']
for ticker in tickers:

    log.info(
        f'extracting src df for ticker: {ticker}')

    res = None

    # get from a date or the latest if not set
    if src_date:
        use_key = f'{ticker}_{src_date}'
        res = ae_extract.extract(
            ticker=ticker,
            date=src_date)
    else:
        res = ae_extract.extract(
            ticker=ticker)

    src_df = res[ticker]['daily']
    fix_key = (
        f'{ticker}_{dst_date}_daily')

    dst_df = fix_df(
        df=src_df)
    log.info(
        f'src df for {ticker} on {src_date}')
    print(src_df)
    log.info(len(src_df.index))
    log.info('-------------')
    log.info(
        f'fixed df for {ticker} on {dst_date}')
    print(dst_df)
    log.info(len(dst_df.index))
    log.info(
        f'publishing fix to redis: {fix_key}')
    pub_res = ae_publish.publish(
        data=dst_df,
        redis_key=fix_key,
        redis_address=use_redis_address,
        df_compress=True,
        verbose=True)

    dst_key = f'{ticker}_{dst_date}'
    ext_res = ae_extract.extract(
        ticker=ticker,
        date=dst_date,
        verbose=False)

    extracted_fix_df = ext_res[ticker]['daily']

    if len(extracted_fix_df.index) == len(dst_df.index):
        log.info(
            'fixed df was published and extracted with the same '
            'row counts: '
            f'len(extracted_fix_df.index) '
            '== '
            f'{len(dst_df.index)}')
    else:
        log.critical(
            'FAILED - fixed df was published and extracted with '
            'different row counts: '
            f'{len(extracted_fix_df.index)} '
            '== '
            f'{len(dst_df.index)}')

        log.error('extracted df')
        print(extracted_fix_df)
        log.error('should be the dst_df')
        print(dst_df)
        log.critical(
            f'tried extracting from key: {use_key}')
        break
# end of for all tickers
