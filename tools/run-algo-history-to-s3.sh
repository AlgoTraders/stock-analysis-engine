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
history_loc=${s3_history_loc}

if [[ "${already_extracted}" == "1" ]]; then
    echo "bypassing extract step - running with: ${extract_loc}"
else
    echo ""
    echo "extracting ${ticker} to ${extract_loc}"
    if [[ "${found_date_params}" == "1" ]]; then
        echo "sa -t ${ticker} -e ${extract_loc} ${use_params}"
        sa -t ${ticker} -e ${extract_loc} ${use_params}
        xerr "Failed to extract ${ticker} between ${start_date} and ${end_date}"
    else
        echo "sa -t ${ticker} -e ${extract_loc} ${use_params}"
        sa -t ${ticker} -e ${extract_loc} ${use_params}
        xerr "Failed to extract ${ticker}"
    fi
fi

echo ""
echo "sa -t ${ticker} -b ${extract_loc} -g ${algo_module_path} -p ${history_loc} ${use_params}"
sa -t ${ticker} -b ${extract_loc} -g ${algo_module_path} -p ${history_loc} ${use_params}
xerr "Failed running ${ticker} backtest with ${extract_loc} using ${algo_module_path} to generate a trading history: ${history_loc}"

echo "Finding extracted algorithm-ready: ${extract_loc}"
show_s3_bucket_for_dataset ${extract_loc}

echo "Finding trading history: ${history_loc}"
show_s3_bucket_for_dataset ${history_loc}

echo ""
echo "run again with:"
echo "sa -t ${ticker} -b ${extract_loc} -g ${algo_module_path} -p ${history_loc} ${use_params}"

exit 0
