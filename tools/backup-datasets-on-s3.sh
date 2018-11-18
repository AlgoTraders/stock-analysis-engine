#!/bin/bash

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

algo_module_path_intraday=/opt/sa/analysis_engine/mocks/example_algo_minute.py
algo_module_path=/opt/sa/analysis_engine/algo.py
algo_name=$(echo ${algo_module_path} | sed -e 's|/| |g' | awk '{print $NF}' | sed -e 's/\.py//g')
algo_version=1

ticker=SPY
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
backtest_start_date=${use_date}
num_days_to_set_start_date="60"
os_type=`uname -s`
distribute_to_workers=""
debug="0"
compose="dev.yml"
extract_loc=""
report_loc=""
history_loc=""
load_loc=""
backup_loc=""
start_date=""
end_date=""
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
transport_scheme="s3://"
dataset_name="${ticker}-${use_date}_BaseAlgo.1_version}_${ds_id}.json"

s3_ready_bucket="algoready"
s3_history_bucket="algohistory"
s3_report_bucket="algoreport"
s3_backup_bucket="backup"

if [[ ! -z "${AWS_ACCESS_KEY_ID}" ]]; then
    export S3_ACCESS_KEY=${AWS_ACCESS_KEY_ID}
fi
if [[ ! -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
    export S3_SECRET_KEY=${AWS_SECRET_ACCESS_KEY}
fi
if [[ -z "${S3_ACCESS_KEY}" ]]; then
    if [[ -z "${AWS_ACCESS_KEY_ID}" ]]; then
        export S3_ACCESS_KEY=trexaccesskey
    else
        export S3_ACCESS_KEY=${AWS_ACCESS_KEY_ID}
    fi
fi
if [[ -z "${S3_SECRET_KEY}" ]] ;then
    if [[ -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        export S3_SECRET_KEY=trex123321
    else
        export S3_SECRET_KEY=${AWS_SECRET_ACCESS_KEY}
        asdf
        exit 1
    fi
fi
if [[ -z "${S3_REGION_NAME}" ]] ;then
    export S3_REGION_NAME=us-east-1
fi
if [[ -z "${S3_SECURE}" ]] ;then
    export S3_SECURE=0
fi
if [[ -z "${S3_BUCKET}" ]] ;then
    export S3_BUCKET=backups
fi
if [[ -z "${REDIS_DB}" ]] ;then
    export REDIS_DB=0
fi

s3_address="${S3_ADDRESS}"
s3_region="${S3_REGION_NAME}"
s3_bucket="${S3_BUCKET}"
redis_address="${REDIS_ADDRESS}"
redis_db="${REDIS_DB}"

# Call getopt to validate the provided input.
while getopts ":t:a:k:e:p:o:l:r:q:i:a:s:n:w:d:u:" o; do
    case "${o}" in
    t)
        ticker=${OPTARG}
        export TICKER=${ticker}
        export DEFAULT_TICKERS=${ticker}
        ;;
    a)
        algo_module_path=${OPTARG}
        algo_name=$(echo ${algo_module_path} | sed -e 's|/| |g' | awk '{print $NF}' | sed -e 's/\.py//g')
        ;;
    e)
        extract_loc=${OPTARG}
        ;;
    p)
        history_loc=${OPTARG}
        ;;
    o)
        report_loc=${OPTARG}
        ;;
    l)
        load_loc=${OPTARG}
        ;;
    r)
        redis_address=${OPTARG}
        export REDIS_ADRESS=${redis_address}
        ;;
    k)
        s3_address=${OPTARG}
        export S3_ADDRESS=${S3_ADDRESS}
        ;;
    q)
        s3_bucket=${OPTARG}
        export S3_BUCKET=${S3_BUCKET}
        ;;
    i)
        export S3_ACCESS_KEY=${OPTARG}
        export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
        ;;
    u)
        export S3_SECRET_KEY=${OPTARG}
        export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"
        ;;
    s)
        start_date=${OPTARG}
        ;;
    n)
        end_date=${OPTARG}
        ;;
    d)
        debug="1"
        ;;
    w)
        distribute_to_workers="-w"
        ;;
    *)
        ;;
    esac
done

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

s3_backup_bucket="${s3_bucket}"
dataset_name="${ticker}-${use_date}_${algo_name}.${algo_version}_${ds_id}.json"
s3_backup_loc=${transport_scheme}${s3_backup_bucket}/${dataset_name}

if [[ "${extract_loc}" != "" ]]; then
    s3_backup_loc=${extract_loc}
fi

echo ""
echo "extracting ${ticker} to ${s3_backup_loc}"
if [[ "${start_date}" != "" ]] && [[ "${end_date}" != "" ]]; then
    echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc} -s ${start_date} -n ${end_date}"
    sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc} -s ${start_date} -n ${end_date}
else
    echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc}"
    sa -t ${ticker} -a ${s3_address} -r ${redis_address} -e ${s3_backup_loc}
fi

test_local=$(echo ${s3_address} | grep localhost | wc -l)
if [[ "${test_local}" == "0" ]]; then
    echo ""
    echo "aws s3 ls s3://${s3_bucket} | grep ${dataset_name}"
    aws s3 ls s3://${s3_bucket} | grep ${dataset_name}
    echo ""
else
    echo ""
    echo "aws --endpoint-url http://localhost:9000 s3 ls s3://${s3_bucket} | grep ${dataset_name}"
    aws --endpoint-url http://localhost:9000 s3 ls s3://${s3_bucket} | grep ${dataset_name}
    echo ""
fi

echo ""
echo "run backtest with custom algo module:"
echo "sa -t ${ticker} -a ${s3_address} -r ${redis_address} -b ${s3_backup_loc} -g /opt/sa/analysis_engine/mocks/example_algo_minute.py"
