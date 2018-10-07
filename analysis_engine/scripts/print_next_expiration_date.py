#!/usr/bin/env python

from analysis_engine.options_dates import get_options_for_today
exp_dates = get_options_for_today()
print(exp_dates[-1]['exp_date_str'])
