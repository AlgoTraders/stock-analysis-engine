#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

echo "---------------------------------"
echo "starting screener-driven analysis"
date -u +"%Y-%m-%d %H:%M:%S"
tickers="$(echo ${DEFAULT_TICKERS} | sed -e 's/,/ /g')"
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

# separate urls with | character:
# export SCREENER_URLS="<url>|<url>|<url>"
if [[ "${SCREENER_URLS}" != "" ]]; then
    echo ""
    echo "starting screeners:"
    echo "fetch -A scn -L ${SCREENER_URLS} -e ${exp_date}"
    fetch -A scn -L ${SCREENER_URLS} -e ${exp_date}
    echo ""
else
    echo "Please set SCREENER_URLS as an environment variable."
    echo "Usage example: SCREENER_URLS=\"<url>|<url>|<url>\""
fi

date -u +"%Y-%m-%d %H:%M:%S"
echo "done"

exit
