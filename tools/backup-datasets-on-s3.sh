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

inf ""
anmt "Running extract ${ticker} and backup to ${s3_backup_loc}"
if [[ "${found_date_params}" == "1" ]]; then
    echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc} ${use_params}"
    sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc} ${use_params}
    xerr "Failed to extract ${ticker} from redis: ${redis_address} to s3: ${s3_address} key: ${s3_backup_loc} with params: ${use_params}"
else
    echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc}"
    sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc}
    xerr "Failed to extract ${ticker} from redis: ${redis_address} to s3: ${s3_address} key: ${s3_backup_loc} and params: ${use_params}"
fi

show_s3_bucket_for_dataset ${s3_backup_loc}

echo ""
echo "run backtest with custom algo module:"
echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -b ${s3_backup_loc} -g ${algo_module_path}"
