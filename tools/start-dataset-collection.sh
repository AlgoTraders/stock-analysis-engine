#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

num_workers=1
log_level=INFO

echo "------------------------"
echo "starting data collection"
date -u +"%Y-%m-%d %H:%M:%S"
tickers="$(echo ${DEFAULT_TICKERS} | sed -e 's/,/ /g')"
exp_date="${EXP_DATE}"
if [[ "${exp_date}" == "" ]]; then
    exp_date="2018-10-19"
fi

use_date=$(date +"%Y-%m-%d")
for ticker in ${tickers}; do
    echo ""
    s3_key="${ticker}_${use_date}"
    echo "run_ticker_analysis.py -t ${ticker} -g all -n ${s3_key} -e ${exp_date}"
    run_ticker_analysis.py -t ${ticker} -g all -n ${s3_key} -e ${exp_date}
done

date -u +"%Y-%m-%d %H:%M:%S"
echo "done"

exit
