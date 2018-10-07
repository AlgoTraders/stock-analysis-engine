#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

echo "------------------------"
echo "starting data collection"
date -u +"%Y-%m-%d %H:%M:%S"
tickers="$(echo ${DEFAULT_TICKERS} | sed -e 's/,/ /g')"
exp_date="${EXP_DATE}"
if [[ "${exp_date}" == "" ]]; then
    if [[ -e /opt/sa/analysis_engine/scripts/print_next_expiration_date.py ]]; then
        exp_date_full=$(/opt/sa/analysis_engine/scripts/print_next_expiration_date.py)
    fi
fi

use_date=$(date +"%Y-%m-%d")
if [[ -e /opt/sa/analysis_engine/scripts/print_last_close_date.py ]]; then
<<<<<<< HEAD
<<<<<<< HEAD
    use_date_str=$(/opt/sa/analysis_engine/scripts/print_last_close_date.py)
    use_date=$(echo ${use_date_str} | awk '{print $1}')
=======
    use_date=$(/opt/sa/analysis_engine/scripts/print_last_close_date.py)
>>>>>>> adding tools for looking up the current option cycle expiration date and the last business close date (not sure Friday holidays are perfect yet though...) these are now used by the distributed automated dataset collection tools to ensure the date on the keys are not Saturday or Sunday datasets (for now)
=======
    use_date_str=$(/opt/sa/analysis_engine/scripts/print_last_close_date.py)
    use_date=$(echo ${use_date_str} | awk '{print $1}')
>>>>>>> fix for data automation
fi

for ticker in ${tickers}; do
    echo ""
    s3_key="${ticker}_${use_date}"
    echo "run_ticker_analysis.py -t ${ticker} -g all -n ${s3_key} -e ${exp_date}"
    run_ticker_analysis.py -t ${ticker} -g all -n ${s3_key} -e ${exp_date}
done

date -u +"%Y-%m-%d %H:%M:%S"
echo "done"

exit
