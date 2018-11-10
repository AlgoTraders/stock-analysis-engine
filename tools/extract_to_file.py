#!/usr/bin/env python

"""
Tool for extracting datasets from
redis for developing and tuning algorithms offline

.. note:: This tool requires redis to be running with
    fetched datasets already stored in supported
    keys
"""

import os
import sys
import json
from analysis_engine.consts import ppj
from analysis_engine.extract import extract

ticker = 'SPY'
res = extract(
    ticker=ticker)

daily_df = res['SPY']['daily']
minute_df = res['SPY']['minute']

out_dir = '/opt/sa/tests/datasets'
if not os.path.exists(out_dir):
    print('missing output dir: {}'.format(
        out_dir))
    sys.exit(1)

daily_file = '{}/{}-daily.json'.format(
    out_dir,
    ticker.lower())
minute_file = '{}/{}-minute.json'.format(
    out_dir,
    ticker.lower())
print('converting dates')

print(
    'converting to pretty printed json file={}'.format(
        daily_file))
daily_out_json = ppj(json.loads(daily_df.iloc[-100:-1].to_json(
    orient='records',
    date_format='iso')))
print(
    'writing to file daily_file={}'.format(
        daily_file))
with open(daily_file, 'w') as f:
    f.write(daily_out_json)

if not os.path.exists(daily_file):
    print('failed creating daily ticker={} daily_file={}'.format(
        ticker,
        daily_file))

print(
    'converting to pretty printed json file={}'.format(
        minute_file))
minute_out_json = ppj(json.loads(minute_df.iloc[-100:-1].to_json(
    orient='records',
    date_format='iso')))
print(
    'writing to file minute_file={}'.format(
        minute_file))
with open(minute_file, 'w') as f:
    f.write(minute_out_json)

if not os.path.exists(minute_file):
    print('failed creating minute ticker={} minute_file={}'.format(
        ticker,
        minute_file))
