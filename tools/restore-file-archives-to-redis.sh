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

data_dir="${1}"
all_archives=$(ls ${data_dir} | grep archive | grep json)

anmt "loading archives from ${data_dir} into redis=${redis_address}"
for f in ${all_archives}; do
    path_to_file="${data_dir}/${f}"
    ticker=$(echo ${f} | sed -e 's/_/ /g' | sed -e 's/-/ /g' | awk '{print $2}')
    inf "sa -t ${ticker} -L ${path_to_file} -r ${redis_address} -m ${redis_db}"
    sa -t ${ticker} -L ${path_to_file} -r ${redis_address} -m ${redis_db}
    xerr "failed to restore archive ${path_to_file} back into redis: ${redis_address}"
done

exit 0
