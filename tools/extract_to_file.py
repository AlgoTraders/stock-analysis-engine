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
    print(f'missing output dir: {out_dir}')
    sys.exit(1)

daily_file = f'{out_dir}/{ticker.lower()}-daily.json'
minute_file = f'{out_dir}/{ticker.lower()}-minute.json'
print('converting dates')

print(f'converting to pretty printed json file={daily_file}')
daily_out_json = ppj(json.loads(daily_df.iloc[-100:-1].to_json(
    orient='records',
    date_format='iso')))
print(f'writing to file daily_file={daily_file}')
with open(daily_file, 'w') as f:
    f.write(daily_out_json)

if not os.path.exists(daily_file):
    print(f'failed creating daily ticker={ticker} daily_file={daily_file}')

print(f'converting to pretty printed json file={minute_file}')
minute_out_json = ppj(json.loads(minute_df.iloc[-100:-1].to_json(
    orient='records',
    date_format='iso')))
print(f'writing to file minute_file={minute_file}')
with open(minute_file, 'w') as f:
    f.write(minute_out_json)

if not os.path.exists(minute_file):
    print(f'failed creating minute ticker={ticker} minute_file={minute_file}')
