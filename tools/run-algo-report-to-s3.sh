#!/bin/bash

algo_module_path=/opt/sa/analysis_engine/mocks/example_algo_minute.py
algo_name=$(echo ${algo_module_path} | sed -e 's|/| |g' | awk '{print $NF}' | sed -e 's/\.py//g')
algo_version=1

ticker=SPY
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
backtest_start_date=${use_date}
num_days_to_set_start_date="60"
os_type=`uname -s`

if [[ "${1}" != "" ]]; then
    ticker="${1}"
fi

# this should be an integer for the number of days back
# to set as the backtest start date
if [[ "${2}" != "" ]]; then
    num_days_to_set_start_date="${2}"
fi

if [[ "${3}" != "" ]]; then
    algo_module_path="${3}"
    algo_name=$(echo ${algo_module_path} | sed -e 's|/| |g' | awk '{print $NF}' | sed -e 's/\.py//g')
fi

distribute_to_workers=""
if [[ "${4}" != "" ]]; then
    distribute_to_workers="-w"
fi

case "$os_type" in
    Linux*)
        backtest_start_date=$(date --date="${num_days_to_set_start_date} day ago" +"%Y-%m-%d")
        ;;
    Darwin*)
        backtest_start_date=$(date -v -${num_days_to_set_start_date}d +"%Y-%m-%d")
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 1
        ;;
esac

if [[ -z "${S3_ACCESS_KEY}" ]]; then
    S3_ACCESS_KEY=trexaccesskey
fi
if [[ -z "${S3_SECRET_KEY}" ]] ;then
    S3_SECRET_KEY=trex123321
fi
if [[ -z "${S3_REGION_NAME}" ]] ;then
    S3_REGION_NAME=us-east-1
fi
if [[ -z "${S3_ADDRESS}" ]] ;then
    S3_ADDRESS=localhost:9000
fi
if [[ -z "${S3_SECURE}" ]] ;then
    S3_SECURE=0
fi
if [[ -z "${S3_BUCKET}" ]] ;then
    S3_BUCKET=algoready
fi
if [[ -z "${REDIS_ADDRESS}" ]] ;then
    REDIS_ADDRESS=localhost:6379
fi
if [[ -z "${REDIS_DB}" ]] ;then
    REDIS_DB=0
fi

transport_scheme="s3://"
s3_ready_bucket="algoready"
s3_history_bucket="algohistory"
s3_report_bucket="algoreport"
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
dataset_name="${ticker}-${use_date}_${algo_name}.${algo_version}_${ds_id}.json"

backtest_loc=${transport_scheme}${s3_ready_bucket}/${dataset_name}
report_loc=${transport_scheme}${s3_report_bucket}/${dataset_name}

test_exists=$(which sa)
if [[ "${test_exists}" == "" ]]; then
    source /opt/venv/bin/activate
    test_exists=$(which sa)
    if [[ "${test_exists}" == "" ]]; then
        echo "Error: unable to find the stock analysis command line tool: sa"
        echo ""
        echo "Please confirm it is is installed from:"
        echo "https://github.com/AlgoTraders/stock-analysis-engine#getting-started"
        echo ""
        exit 1
    fi
fi

echo ""
echo "extracting ${ticker} to ${backtest_loc}"
echo "sa -t ${ticker} -e ${backtest_loc}"
sa -t ${ticker} -e ${backtest_loc}

echo ""
echo ""
echo "sa -t ${ticker} -b ${backtest_loc} -g ${algo_module_path} -o ${report_loc}"
sa -t ${ticker} -b ${backtest_loc} -g ${algo_module_path} -o ${report_loc}

echo ""
echo "aws --endpoint-url http://localhost:9000 s3 ls s3://algoreport | grep ${dataset_name}"
aws --endpoint-url http://localhost:9000 s3 ls s3://algoreport | grep ${dataset_name}
echo ""

echo ""
echo "run again in the future with:"
echo "sa -t ${ticker} -b ${backtest_loc} -g ${algo_module_path} -o ${report_loc}"

exit 0
