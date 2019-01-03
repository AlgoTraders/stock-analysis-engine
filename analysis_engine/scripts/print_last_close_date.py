#!/usr/bin/env python

from analysis_engine.utils import last_close
last_close_str = last_close().strftime('%Y-%m-%d %H:%M:%S')
print(last_close_str)
