#!/bin/bash

test_exists=$(which fetch)
if [[ "${test_exists}" == "" ]]; then
    source /opt/venv/bin/activate
    test_exists=$(which fetch)
    if [[ "${test_exists}" == "" ]]; then
        echo "Error: unable to find the stock analysis command line tool: fetch"
        echo ""
        echo "Please confirm it is is installed from:"
        echo "https://github.com/AlgoTraders/stock-analysis-engine#getting-started"
        echo ""
        exit 1
    fi
fi

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

echo "---------------------------"
echo "starting dataset collection"
date -u +"%Y-%m-%d %H:%M:%S"

tickers="SPY"
celery_enabled=""
if [[ "${1}" != "" ]]; then
    tickers="${1}"
else
    if [[ "${DEFAULT_TICKERS}" != "" ]]; then
        # run inside docker or kubernetes with a decoupled engine
        celery_enabled="-Z"
        tickers="$(echo ${DEFAULT_TICKERS} | sed -e 's/,/ /g')"
    fi
fi

exp_date="${EXP_DATE}"
if [[ "${exp_date}" == "" ]]; then
    if [[ -e /opt/sa/analysis_engine/scripts/print_next_expiration_date.py ]]; then
        exp_date=$(/opt/sa/analysis_engine/scripts/print_next_expiration_date.py)
    fi
fi

use_date=$(date +"%Y-%m-%d")
if [[ -e /opt/sa/analysis_engine/scripts/print_last_close_date.py ]]; then
    use_date_str=$(/opt/sa/analysis_engine/scripts/print_last_close_date.py)
    use_date=$(echo ${use_date_str} | awk '{print $1}')
fi

dataset_sources="initial"
if [[ "${DATASET_SOURCES}" != "" ]]; then
    dataset_sources="${DATASET_SOURCES}"
fi

for ticker in ${tickers}; do
    echo ""
    s3_key="${ticker}_${use_date}"
    echo "fetch -t ${ticker} -g ${dataset_sources} -n ${s3_key} -e ${exp_date} ${celery_enabled}"
    fetch -t ${ticker} -g ${dataset_sources} -n ${s3_key} -e ${exp_date} ${celery_enabled}
done

date -u +"%Y-%m-%d %H:%M:%S"
echo "done"

exit
