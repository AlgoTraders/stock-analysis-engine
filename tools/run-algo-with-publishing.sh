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

extract_loc=${s3_extract_loc}
history_loc=${s3_extract_loc}
report_loc=${s3_report_loc}

echo ""
echo "extracting backtest algorithm-ready dataset for: ${ticker} id: ${dataset_name} for date range: ${start_date} to ${use_date} with s3: ${extract_loc}"
echo "sa -t ${ticker} -e ${extract_loc} -s ${start_date} -n ${use_date}"
sa -t ${ticker} -e ${extract_loc} -s ${start_date} -n ${use_date}

echo ""
echo "running backtest algorithm-ready dataset for: ${ticker} id: ${dataset_name} for date range: ${start_date} to ${use_date} with s3: ${extract_loc}"
echo "sa -t ${ticker} -p ${history_loc} -o ${report_loc} -b ${extract_loc} -s ${start_date} -n ${use_date}"
sa -t ${ticker} -p ${history_loc} -o ${report_loc} -b ${extract_loc} -s ${start_date} -n ${use_date}

test_exists=$(which aws)
if [[ "${test_exists}" != "" ]]; then
    echo ""
    echo "Getting ${ticker} Algorithm-Ready datasets in s3://algoready:"
    aws --endpoint-url http://localhost:9000 s3 ls s3://algoready | grep ${dataset_name}
    echo ""
    echo "Getting ${ticker} Algorithm-Ready datasets in s3://algoready:"
    aws --endpoint-url http://localhost:9000 s3 ls s3://algoready | grep ${dataset_name}
    echo ""
    echo "Getting ${ticker} Algorithm-Ready datasets (for backtests) in s3://algoready:"
    aws --endpoint-url http://localhost:9000 s3 ls s3://algoready | grep ${dataset_name}
fi

echo ""
echo "run again in the future with:"
echo "sa -t ${ticker} -p ${history_loc} -o ${report_loc} -b ${extract_loc} -s ${start_date} -n ${use_date}"
sa -t ${ticker} -p ${history_loc} -o ${report_loc} -b ${extract_loc} -s ${start_date} -n ${use_date}

exit 0
