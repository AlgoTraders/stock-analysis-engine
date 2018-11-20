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

use_tickers=$(echo ${DEFAULT_TICKERS} | sed -e 's|,| |g')
echo "Running archival job for tickers: ${use_tickers} to ${S3_ADDRESS} in bucket: ${S3_BUCKET}"
for ticker in ${use_tickers}; do
    echo "Archiving ${ticker} to ${S3_ADDRESS}"
    s3_backup_key="s3://${S3_BUCKET}/archive_${ticker}-${use_date}.json"
    echo "/opt/sa/tools/backup-datasets-on-s3.sh -t ${ticker} -q ${S3_BUCKET} -e ${s3_backup_key}"
    /opt/sa/tools/backup-datasets-on-s3.sh -t ${ticker} -q ${S3_BUCKET} -e ${s3_backup_key}
done

echo "Done running archival job for tickers: ${use_tickers} to ${S3_ADDRESS} in bucket: ${S3_BUCKET}"

exit 0
