#!/bin/bash

ticker=SPY
backtest_start_date=$(date --date="1 day ago" +"%Y-%m-%d")

if [[ "${1}" != "" ]]; then
    ticker="${1}"
fi

# this should be an integer for the number of days back
# to set as the backtest start date
if [[ "${2}" != "" ]]; then
    backtest_start_date=$(date --date="${2} day ago" +"%Y-%m-%d")
fi

use_date=$(date +"%Y-%m-%d")
ticker_dataset="${ticker}-${use_date}.json"
echo "creating ${ticker} dataset: ${ticker_dataset} dates: ${backtest_start_date} to ${use_date}"
report_loc="s3://algoreports/${ticker_dataset}"
history_loc="s3://algohistory/${ticker_dataset}"
report_loc="s3://algoreport/${ticker_dataset}"
extract_loc="s3://algoready/${ticker_dataset}"
backtest_loc="file:/tmp/${ticker_dataset}"
echo "running algo with:"

echo "sa -t SPY -e ${report_loc} -p ${history_loc} -o ${report_loc} -w ${extract_loc} -b ${backtest_loc} -s ${backtest_start_date} -n ${use_date}"

test_exists=$(which sa)
if [[ "${test_exists}" == "" ]]; then
    source /opt/venv/bin/activate
fi
sa -t SPY -p ${history_loc} -o ${report_loc} -e ${extract_loc} -b ${backtest_loc} -s ${backtest_start_date} -n ${use_date}

exit 0
