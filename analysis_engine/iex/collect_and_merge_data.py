"""
Get Pricing using most of the pieces of example from:
https://github.com/timkpaine/hedgedata/blob/master/scripts/fetch_data.py

This will fetch various pricing, financials, earnings,
dividends, news and other data from
`IEX <https://iexcloud.io/>`__.

Data Attribution
================

IEX Real-Time Price
===================

- Cite IEX using the following text and link:
  "Data provided by [IEX](https://iextrading.com/developer/docs/)."
- Provide a link to
  https://iextrading.com/api-exhibit-a in your terms of service.
- Additionally, if you display our TOPS price data,
  cite "IEX Real-Time Price" near the price.

"""

import os
import os.path
import pandas as pd
import analysis_engine.iex.consts
from hedgedata.backfill import whichBackfill
from hedgedata.data import FIELDS
from hedgedata.distributor import Distributer
from spylunking.log.setup_logging import build_colorized_logger
# from hedgedata import sp500_constituents


log = build_colorized_logger(
    name=__name__)


_DISTRIBUTOR = Distributer.default()


def backfillData(
        distributor,
        symbols,
        fields,
        output='cache'):
    """backfillData

    :param distributor: distributor object from:
                        https://github.com/timkpaine/hedgedata
    :param symbols: list of symbols to iterate
    :param fields: path to files
    :param output: output dir
    """
    if not os.path.exists(output):
        os.makedirs(output)

    for field in fields:
        if os.path.exists(os.path.join(output, field) + '.csv'):
            data_orig = pd.read_csv(os.path.join(output, field) + '.csv')
            for k in (
                    'date',
                    'datetime',
                    'reportDate',
                    'EPSReportDate',
                    'exDate'):
                if k in data_orig.columns:
                    data_orig[k] = pd.to_datetime(data_orig[k])

        else:
            data_orig = pd.DataFrame()

        for symbol, data in whichBackfill(field)(_DISTRIBUTOR, symbols):
            if data.empty:
                log.critical('Skipping %s for %s' % (symbol, field))
                continue

            log.critical('Filling %s for %s' % (symbol, field))
            data.reset_index(inplace=True)

            if field == 'PEERS':
                data = data[['peer']]

            data['KEY'] = symbol
            data_orig = pd.concat(
                [data_orig, data]) if not data_orig.empty else data

        if not data_orig.empty:
            data_orig.set_index(
                analysis_engine.iex.consts.get_default_fields(
                    field),
                inplace=True)
            data_orig[
                ~data_orig.index.duplicated(
                    keep='first')].to_csv(
                        os.path.join(output, field) + '.csv')


if __name__ == '__main__':
    syms = [
        'SPY',
        'AMZN',
        'TLSA',
        'NFLX'
    ]
    backfillData(
        symbols=syms,
        fields=FIELDS,
        output='./cache')
