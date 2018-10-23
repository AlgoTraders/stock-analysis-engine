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

# separate urls with | character:
# export SCREENER_URLS="<url>|<url>|<url>"
if [[ "${SCREENER_URLS}" != "" ]]; then
    echo ""
    echo "starting screeners:"
    echo "run_ticker_analysis.py -A scn -L ${SCREENER_URLS} -e ${exp_date}"
    run_ticker_analysis.py -A scn -L ${SCREENER_URLS} -e ${exp_date}
    echo ""
else
    echo "Please set SCREENER_URLS as an environment variable."
    echo "Usage example: SCREENER_URLS=\"<url>|<url>|<url>\""
fi

date -u +"%Y-%m-%d %H:%M:%S"
echo "done"

exit
