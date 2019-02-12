#!/bin/bash

if [[ -e /opt/sa/analysis_engine/scripts/backtest_parsing_env.sh ]]; then
    source /opt/sa/analysis_engine/scripts/backtest_parsing_env.sh
elif [[ -e ./analysis_engine/scripts/backtest_parsing_env.sh ]]; then
    source ./analysis_engine/scripts/backtest_parsing_env.sh
elif [[ "${PATH_TO_AE_ENV}" != "" ]]; then
    if [[ -e "${PATH_TO_AE_ENV}" ]]; then
        source ${PATH_TO_AE_ENV}
    fi
fi

# start custom handling where args, variables and environment
# variables are set:
# https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/backtest_parsing_env.sh
# 
# debug this script's parsing of arguments with: -d 

arg_ticker="${1}"
if [[ "${arg_ticker}" == "" ]]; then
    err "Usage error - please run with a ticker: backfill-minute-data.sh TICKER"
    exit 1
fi
ticker=$(echo ${arg_ticker} | awk '{print toupper($0)}')

num_days=30
start_date=""
case "$os_type" in
    Linux*)
        start_date=$(date --date="${num_days} day ago" +"%Y-%m-%d")
        ;;
    Darwin*)
        start_date=$(date -v -${num_days}d +"%Y-%m-%d")
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 1
        ;;
esac

today=$(date +"%Y-%m-%d")
echo ""
anmt "--------------------------------"
anmt "Backfilling minute data for ${ticker} between ${start_date} to ${today}"

days_back=0
while [[ $days_back -ne ${num_days} ]]; do
    cur_date=""
    day_of_week=$(date +"%a")
    if [[ ${days_back} -eq 0 ]]; then
        cur_date="${today}"
    else
        case "$os_type" in
            Linux*)
                cur_date=$(date --date="${days_back} day ago" +"%Y-%m-%d")
                day_of_week=$(date --date="${days_back} day ago" +"%a")
                ;;
            Darwin*)
                cur_date=$(date -v -${days_back}d +"%Y-%m-%d")
                day_of_week=$(date -v -${days_back}d +"%a")
                ;;
            *)
                warn "Unsupported OS, exiting."
                exit 1
                ;;
        esac
    fi

    if [[ "${day_of_week}" != "Sat" ]] && [[ "${day_of_week}" != "Sun" ]]; then
        inf " - Fetching IEX Cloud minute data for ${ticker} on ${cur_date} with:"
        echo "fetch -t ${ticker} -F ${cur_date} -g iex_min"
        fetch -t ${ticker} -F ${cur_date} -g iex_min
        if [[ "$?" != "0" ]]; then
            err "Stopping - failed fetching ${ticker} on ${cur_date}"
            exit 1
        fi
    else
        inf " - Skipping ${day_of_week}"
    fi

    let "days_back=days_back+1"

done

good "Done backfilling minute data for ${ticker} between ${start_date} to ${today}"

exit 0
