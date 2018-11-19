# used for parsing backtesting command line tools
# to load it use:
# source /opt/sa/analysis_engine/scripts/backtest_parsing_env.sh
# or:
# . /opt/sa/analysis_engine/scripts/backtest_parsing_env.sh
#
# Debug this file with:
# export DEBUG_AE=1

if [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
elif [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
else
    found_good_common="0"
    if [[ "${USE_AS_BASH_COMMON}" == "" ]]; then
        if [[ -e "${USE_AS_BASH_COMMON}" ]]; then
            source ${USE_AS_BASH_COMMON}
            found_good_common="1"
        fi
    fi

    if [[ "${found_good_common}" == "0" ]]; then
        inf() {
            echo "$@"
        }
        anmt() {
            echo "$@"
        }
        good() {
            echo "$@"
        }
        err() {
            echo "$@"
        }
        critical() {
            echo "$@"
        }
        warn() {
            echo "$@"
        }
    fi
fi

test_exists=$(which sa)
if [[ "${test_exists}" == "" ]]; then
    source /opt/venv/bin/activate
    test_exists=$(which sa)
    if [[ "${test_exists}" == "" ]]; then
        if [[ "${USE_VENV}" != "" ]]; then
            source ${USE_VENV}
        fi
        test_exists=$(which sa)
        if [[ "${test_exists}" == "" ]]; then
            err "Error: unable to find the stock analysis command line tool: sa"
            err ""
            err "Please confirm it is is installed from:"
            err "https://github.com/AlgoTraders/stock-analysis-engine#getting-started"
            err ""
            exit 1
        fi
    fi
fi

algo_module_path_intraday=/opt/sa/analysis_engine/mocks/example_algo_minute.py
algo_base_module_path=/opt/sa/analysis_engine/algo.py
algo_module_path=/opt/sa/analysis_engine/algo.py
algo_name=$(echo ${algo_module_path} | sed -e 's|/| |g' | sed -e 's|_|-|g' | awk '{print $NF}' | sed -e 's/\.py//g')
algo_version=1
algo_config_file=""

ticker=SPY
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
backtest_start_date=${use_date}
num_days_to_set_start_date="60"
os_type=`uname -s`
distribute_to_workers=""
debug="0"
already_extracted="0"
extract_loc=""
report_loc=""
history_loc=""
load_loc=""
backup_loc=""
start_date=""
end_date=""
use_date=$(date +"%Y-%m-%d")
ds_id=$(uuidgen | sed -e 's/-//g')
dataset_name="${ticker}-${use_date}_BaseAlgo.1_version}_${ds_id}.json"
s3_transport_scheme="s3://"
file_transport_scheme="file:"
redis_transport_scheme="redis://"

use_custom_bucket=""
use_extract_loc=""
use_backup_loc=""
use_history_loc=""
use_report_loc=""
use_load_loc=""

redis_address="localhost:6379"
redis_db="0"
s3_address="localhost:9000"
s3_region_name="us-east-1"
s3_secure="0"
s3_bucket="MISSING_AN_S3_BUCKET"
s3_ready_bucket="algoready"
s3_extract_bucket="algoready"
s3_history_bucket="algohistory"
s3_report_bucket="algoreport"
s3_backup_bucket="algobackup"

file_ready_dir="/tmp"
file_extract_dir="/tmp"
file_history_dir="/tmp"
file_report_dir="/tmp"
file_backup_dir="/tmp"

redis_extract_address="localhost:6379"
redis_ready_address="localhost:6379"
redis_history_address="localhost:6379"
redis_report_address="localhost:6379"
redis_backup_address="localhost:6379"

if [[ ! -z "${AWS_ACCESS_KEY_ID}" ]]; then
    export S3_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
fi
if [[ ! -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
    export S3_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
fi
if [[ -z "${S3_ACCESS_KEY}" ]]; then
    if [[ -z "${AWS_ACCESS_KEY_ID}" ]]; then
        export S3_ACCESS_KEY=trexaccesskey
    else
        export S3_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
    fi
fi
if [[ -z "${S3_SECRET_KEY}" ]] ;then
    if [[ -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        export S3_SECRET_KEY=trex123321
    else
        export S3_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
    fi
fi
if [[ -z "${S3_ADDRESS}" ]] ;then
    export S3_ADDRESS=${s3_address}
fi
if [[ -z "${S3_REGION_NAME}" ]] ;then
    export S3_REGION_NAME=${s3_region_name}
fi
if [[ -z "${S3_SECURE}" ]] ;then
    export S3_SECURE=${s3_secure}
fi
if [[ -z "${S3_BUCKET}" ]] ;then
    export S3_BUCKET="${s3_bucket}"
fi
if [[ -z "${REDIS_ADDRESS}" ]] ;then
    export REDIS_ADDRESS=${redis_address}
fi
if [[ -z "${REDIS_DB}" ]] ;then
    export REDIS_DB=${redis_db}
fi
if [[ -z "${NUM_DAYS_BACK}" ]] ;then
    export NUM_DAYS_BACK="${num_days_to_set_start_date}"
fi
if [[ -z "${BACKTEST_END_DATE}" ]] ;then
    export BACKTEST_END_DATE="${use_date}"
fi
if [[ "${ALGO_READY_DATASET_S3_BUCKET_NAME}" != "" ]]; then
    s3_ready_bucket="${ALGO_READY_DATASET_S3_BUCKET_NAME}"
fi
if [[ "${ALGO_HISTORY_DATASET_S3_BUCKET_NAME}" != "" ]]; then
    s3_history_bucket="${ALGO_HISTORY_DATASET_S3_BUCKET_NAME}"
fi
if [[ "${ALGO_EXTRACT_DATASET_S3_BUCKET_NAME}" != "" ]]; then
    s3_extract_bucket="${ALGO_EXTRACT_DATASET_S3_BUCKET_NAME}"
fi
if [[ "${ALGO_REPORT_DATASET_S3_BUCKET_NAME}" != "" ]]; then
    s3_report_bucket="${ALGO_REPORT_DATASET_S3_BUCKET_NAME}"
fi
if [[ "${ALGO_BACKUP_DATASET_S3_BUCKET_NAME}" != "" ]]; then
    s3_backup_bucket="${ALGO_BACKUP_DATASET_S3_BUCKET_NAME}"
fi
if [[ "${ALGO_READY_DIR}" != "" ]]; then
    file_ready_dir="${ALGO_READY_DIR}"
fi
if [[ "${ALGO_EXTRACT_DIR}" != "" ]]; then
    file_extract_dir="${ALGO_EXTRACT_DIR}"
fi
if [[ "${ALGO_HISTORY_DIR}" != "" ]]; then
    file_history_dir="${ALGO_HISTORY_DIR}"
fi
if [[ "${ALGO_REPORT_DIR}" != "" ]]; then
    file_report_dir="${ALGO_REPORT_DIR}"
fi
if [[ "${ALGO_BACKUP_DIR}" != "" ]]; then
    file_backup_dir="${ALGO_BACKUP_DIR}"
fi
if [[ "${ALGO_READY_REDIS_ADDRESS}" != "" ]]; then
    redis_ready_address="${ALGO_READY_REDIS_ADDRESS}"
fi
if [[ "${ALGO_EXTRACT_REDIS_ADDRESS}" != "" ]]; then
    redis_extract_address="${ALGO_EXTRACT_REDIS_ADDRESS}"
fi
if [[ "${ALGO_HISTORY_REDIS_ADDRESS}" != "" ]]; then
    redis_history_address="${ALGO_HISTORY_REDIS_ADDRESS}"
fi
if [[ "${ALGO_REPORT_REDIS_ADDRESS}" != "" ]]; then
    redis_report_address="${ALGO_REPORT_REDIS_ADDRESS}"
fi
if [[ "${ALGO_BACKUP_REDIS_ADDRESS}" != "" ]]; then
    redis_backup_address="${ALGO_BACKUP_REDIS_ADDRESS}"
fi

s3_address="${S3_ADDRESS}"
s3_region_name="${S3_REGION_NAME}"
s3_bucket="${S3_BUCKET}"
redis_address="${REDIS_ADDRESS}"
redis_db="${REDIS_DB}"

usage() {
    err "Error: invalid argument caused a usage error"
    anmt "Supported arguments:"
    echo ""
    echo " -t TICKER - stock/etf symbol for the backtest"
    if [[ "${TICKER}" != "" ]]; then
        anmt "    using: -t ${TICKER}"
    fi
    echo " -a ALGORITHM_MODULE_PATH - optional - file path to a custom algorithm (default BaseAlgo is: /opt/sa/analysis_engine/algo.py)"
    if [[ "${ALGORITHM_MODULE_PATH}" != "" ]]; then
        anmt "    using: -a ${ALGORITHM_MODULE_PATH}"
    fi
    echo " -e EXTRACT_LOCATION - optional - extract algorithm-ready dataset and publish to s3/redis/file location"
    if [[ "${EXTRACT_LOCATION}" != "" ]]; then
        anmt "    using: -e ${EXTRACT_LOCATION}"
    fi
    echo " -p HISTORY_LOCATION - optional - publish algorithm trading history dataset to s3/redis/file location"
    if [[ "${HISTORY_LOCATION}" != "" ]]; then
        anmt "    using: -p ${HISTORY_LOCATION}"
    fi
    echo " -o REPORT_LOCATION - optional - publish algorithm trading performance report dataset to s3/redis/file location"
    if [[ "${REPORT_LOCATION}" != "" ]]; then
        anmt "    using: -o ${REPORT_LOCATION}"
    fi
    echo " -l LOAD_LOCATION - optional - load an algorithm-ready dataset from s3/redis/file location"
    if [[ "${LOAD_LOCATION}" != "" ]]; then
        anmt "    using: -l ${LOAD_LOCATION}"
    fi
    echo " -r REDIS_ADDRESS - host:port for redis (default localhost:6379 and K8 is redis-master:6379)"
    if [[ "${REDIS_ADDRESS}" != "" ]]; then
        anmt "    using: -r ${REDIS_ADDRESS}"
    fi
    echo " -f REDIS_DB - redis database (optional - default 0)"
    if [[ "${REDIS_DB}" != "" ]]; then
        anmt "    using: -f ${REDIS_DB}"
    fi
    echo " -R REDIS_PASSWORD - (optional - default None - omit this argument unless redis has a password on it)"
    echo " -i AWS_ACCESS_KEY_ID - access key for minio or AWS (default trexaccesskey)"
    echo " -u AWS_SECRET_ACCESS_KEY - secret key for minio or AWS (default trex123321)"
    echo " -k S3_ADDRESS - host:port for minio or AWS (default localhost:9000 and K8 is example.minio.com:9000 and AWS is: s3.us-east-1.amazonaws.com)"
    if [[ "${S3_ADDRESS}" != "" ]]; then
        anmt "    using: -k ${S3_ADDRESS}"
    fi
    echo " -x S3_REGION_NAME - S3 region (optional - default us-east-1)"
    if [[ "${S3_REGION_NAME}" != "" ]]; then
        anmt "    using: -x ${S3_REGION_NAME}"
    fi
    echo " -q S3_BUCKET - S3 bucket name"
    if [[ "${S3_BUCKET}" != "" ]]; then
        anmt "    using: -q ${S3_BUCKET}"
    fi
    echo " -K S3_SECURE - tls required (optional - default off, turn on with: -K 1)"
    if [[ "${S3_SECURE}" != "" ]]; then
        anmt "    using: -K ${S3_SECURE}"
    fi
    echo " -c ALGORITHM_CONFIG_FILE - option - config file with custom algorithm configuration data (indicator config and buy/sell strategy rules)"
    if [[ "${ALGORITHM_CONFIG_FILE}" != "" ]]; then
        anmt "    using: -c ${ALGORITHM_CONFIG_FILE}"
    fi
    echo " -s BACKTEST_START_DATE - start the backtest on this date (optional - default 60 days before today format: YYYY-MM-DD)"
    if [[ "${BACKTEST_START_DATE}" != "" ]]; then
        anmt "    using: -s ${BACKTEST_START_DATE}"
    fi
    echo " -n BACKTEST_END_DATE - end the backtest on this date (default - today or a date with format: YYYY-MM-DD)"
    if [[ "${BACKTEST_END_DATE}" != "" ]]; then
        anmt "    using: -n ${BACKTEST_END_DATE}"
    fi
    echo " -b NUM_DAYS_BACK - number of days to set the start date behind the today or the use_date"
    if [[ "${NUM_DAYS_BACK}" != "" ]]; then
        anmt "    using: -b ${NUM_DAYS_BACK}"
    fi
    echo " -z - flag - bypass any starting extraction steps"
    echo " -w - flag - distribute the jobs by publishing to remote engine workers"
    echo " -d - flag - debug mode (enable with: -d)"
    echo ""
    warn "If you believe this is an error, please reach out on GitHub (slack is coming soon): "
    echo "https://github.com/AlgoTraders/stock-analysis-engine/issues/new"
    echo ""
    anmt "Here are some commands to help troubleshoot issues:"
    echo "which python"
    echo "pip freeze"
    echo "uname -s"
    echo ""
}

# Call getopt to validate the provided input.
while getopts ":t:a:e:p:o:l:r:R:f:k:x:q:i:u:K:s:n:b:c:zwdj" o; do
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
        use_extract_loc="${OPTARG}"
        use_backup_loc="${OPTARG}"
        ;;
    p)
        history_loc=${OPTARG}
        use_history_loc="${OPTARG}"
        ;;
    o)
        report_loc=${OPTARG}
        use_report_loc="${OPTARG}"
        ;;
    l)
        load_loc=${OPTARG}
        use_load_loc="${OPTARG}"
        ;;
    r)
        redis_address=${OPTARG}
        export REDIS_ADRESS=${redis_address}
        ;;
    R)
        redis_password=${OPTARG}
        export REDIS_PASSWORD=${redis_password}
        ;;
    f)
        redis_db=${OPTARG}
        export REDIS_DB=${redis_db}
        ;;
    k)
        s3_address=${OPTARG}
        export S3_ADDRESS=${s3_address}
        ;;
    x)
        s3_region_name=${OPTARG}
        export S3_REGION_NAME=${s3_region_name}
        export AWS_DEFAULT_REGION=${s3_region_name}
        ;;
    q)
        s3_bucket=${OPTARG}
        export S3_BUCKET=${s3_bucket}
        use_custom_bucket=${s3_bucket}
        ;;
    i)
        export S3_ACCESS_KEY=${OPTARG}
        export AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY}"
        ;;
    u)
        export S3_SECRET_KEY=${OPTARG}
        export AWS_SECRET_ACCESS_KEY="${S3_SECRET_KEY}"
        ;;
    K)
        s3_secure=1
        export S3_SECURE="1"
        ;;
    s)
        start_date=${OPTARG}
        export BACKTEST_START_DATE=${start_date}
        ;;
    n)
        end_date=${OPTARG}
        export BACKTEST_END_DATE=${end_date}
        ;;
    b)
        num_days_to_set_start_date=${OPTARG}
        export NUM_DAYS_BACK=${num_days_to_set_start_date}
        ;;
    c)
        algo_config_file=${OPTARG}
        export ALGO_CONFIG_FILE=${OPTARG}
        ;;
    z)
        already_extracted="1"
        export ALREADY_EXTRACTED="1"
        ;;
    d)
        debug="1"
        export DEBUG_AE="1"
        ;;
    w)
        distribute_to_workers="-w"
        ;;
    *)
        usage
        exit 1
        ;;
    esac
done

case "$os_type" in
    Linux*)
        backtest_start_date=$(date --date="${num_days_to_set_start_date} day ago" +"%Y-%m-%d")
        start_date=${backtest_start_date}
        ;;
    Darwin*)
        backtest_start_date=$(date -v -${num_days_to_set_start_date}d +"%Y-%m-%d")
        start_date=${backtest_start_date}
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 1
        ;;
esac

# Defaults:

dataset_name="${ticker}-${use_date}_${algo_name}.${algo_version}_${ds_id}.json"

if [[ "${use_load_loc}" != "" ]]; then
    s3_load_loc="${use_load_loc}"
    file_load_loc="${use_load_loc}"
    redis_load_loc="${use_load_loc}"
else
    s3_load_loc="${s3_transport_scheme}${s3_ready_bucket}/${dataset_name}"
    file_load_loc="${file_transport_scheme}${file_ready_dir}/${dataset_name}"
    redis_load_loc="${redis_transport_scheme}${redis_ready_address}/${dataset_name}"
fi

# publishing sets the dataset_name based off the key on any arg value

if [[ "${use_extract_loc}" != "" ]]; then
    s3_extract_loc="${use_extract_loc}"
    file_extract_loc="${use_extract_loc}"
    redis_extract_loc="${use_extract_loc}"
    dataset_name=$(echo ${use_extract_loc} | sed -e 's|/| |g' | awk '{print $NF}')
else
    s3_extract_loc="${s3_transport_scheme}${s3_ready_bucket}/${dataset_name}"
    file_extract_loc="${file_transport_scheme}${file_ready_dir}/${dataset_name}"
    redis_extract_loc="${redis_transport_scheme}${redis_extract_address}/${dataset_name}"
fi

if [[ "${use_report_loc}" != "" ]]; then
    s3_report_loc="${use_report_loc}"
    file_report_loc="${use_report_loc}"
    redis_report_loc="${use_report_loc}"
    dataset_name=$(echo ${use_report_loc} | sed -e 's|/| |g' | awk '{print $NF}')
else
    s3_report_loc="${s3_transport_scheme}${s3_report_bucket}/${dataset_name}"
    file_report_loc="${file_transport_scheme}${file_report_dir}/${dataset_name}"
    redis_report_loc="${redis_transport_scheme}${redis_report_address}/${dataset_name}"
fi

if [[ "${use_history_loc}" != "" ]]; then
    s3_history_loc="${use_history_loc}"
    file_history_loc="${use_history_loc}"
    redis_history_loc="${use_history_loc}"
    dataset_name=$(echo ${use_history_loc} | sed -e 's|/| |g' | awk '{print $NF}')
else
    s3_history_loc="${s3_transport_scheme}${s3_history_bucket}/${dataset_name}"
    file_history_loc="${file_transport_scheme}${file_history_dir}/${dataset_name}"
    redis_history_loc="${redis_transport_scheme}${redis_history_address}/${dataset_name}"
fi

if [[ "${use_backup_loc}" != "" ]]; then
    s3_backup_loc="${use_backup_loc}"
    file_backup_loc="${use_backup_loc}"
    redis_backup_loc="${use_backup_loc}"
    dataset_name=$(echo ${use_backup_loc} | sed -e 's|/| |g' | awk '{print $NF}')
else
    s3_backup_loc="${s3_transport_scheme}${s3_backup_bucket}/${dataset_name}"
    file_backup_loc="${file_transport_scheme}${file_backup_dir}/${dataset_name}"
    redis_backup_loc="${redis_transport_scheme}${redis_backup_address}/${dataset_name}"
fi

if [[ "${use_custom_bucket}" != "" ]]; then
    s3_extract_loc="${s3_transport_scheme}${use_custom_bucket}/${dataset_name}"
    s3_report_loc="${s3_transport_scheme}${s3_report_bucket}/${dataset_name}"
    s3_history_loc="${s3_transport_scheme}${use_custom_bucket}/${dataset_name}"
    s3_backup_loc="${s3_transport_scheme}${use_custom_bucket}/${dataset_name}"
fi

# Environment variables:

# Algorithms:
export ALGO_MODULE_PATH="${algo_module_path}"
export ALGO_NAME="${algo_name}"
export ALGO_VERSION="${algo_version}"
export ALGO_CONFIG_FILE=${algo_config_file}

# Backtests
export BACKTEST_START_DATE=${backtest_start_date}

# Datasets:
export DATASET_NAME="${ticker}-${use_date}_${algo_name}.${algo_version}_${ds_id}.json"

# Datasets on s3:
export S3_EXTRACT_LOC="${s3_extract_loc}"
export S3_LOAD_LOC="${s3_load_loc}"
export S3_REPORT_LOC="${s3_report_loc}"
export S3_HISTORY_LOC="${s3_history_loc}"
export S3_BACKUP_LOC="${s3_backup_loc}"

# Datasets as local files:
export FILE_EXTRACT_LOC="${file_extract_loc}"
export FILE_LOAD_LOC="${file_load_loc}"
export FILE_REPORT_LOC="${file_report_loc}"
export FILE_HISTORY_LOC="${file_history_loc}"
export FILE_BACKUP_LOC="${file_backup_loc}"

# Datasets in redis:
export REDIS_EXTRACT_LOC="${redis_extract_loc}"
export REDIS_LOAD_LOC="${redis_load_loc}"
export REDIS_REPORT_LOC="${redis_report_loc}"
export REDIS_HISTORY_LOC="${redis_history_loc}"
export REDIS_BACKUP_LOC="${redis_backup_loc}"

show_algo_env() {
    echo ""
    anmt "Analysis Engine Environment Variables"
    anmt "-------------------------------------"
    date +"%Y-%m-%d %H:%m:%s"
    echo ""
    good "Datasets in Redis:"
    inf "- REDIS_ADDRESS: ${REDIS_ADDRESS}"
    inf "- REDIS_DB: ${REDIS_DB}"
    inf "- REDIS_EXTRACT_LOC: ${REDIS_EXTRACT_LOC}"
    inf "- REDIS_LOAD_LOC: ${REDIS_LOAD_LOC}"
    inf "- REDIS_REPORT_LOC: ${REDIS_REPORT_LOC}"
    inf "- REDIS_HISTORY_LOC: ${REDIS_HISTORY_LOC}"
    inf "- REDIS_BACKUP_LOC: ${REDIS_BACKUP_LOC}"
    echo ""
    good "Datasets as local files:"
    inf "- FILE_EXTRACT_LOC: ${FILE_EXTRACT_LOC}"
    inf "- FILE_LOAD_LOC: ${FILE_LOAD_LOC}"
    inf "- FILE_REPORT_LOC: ${FILE_REPORT_LOC}"
    inf "- FILE_HISTORY_LOC: ${FILE_HISTORY_LOC}"
    inf "- FILE_BACKUP_LOC: ${FILE_BACKUP_LOC}"
    echo ""
    good "Datasets on S3:"
    inf "- S3_ADDRESS: ${S3_ADDRESS}"
    inf "- S3_REGION_NAME: ${S3_REGION_NAME}"
    inf "- S3_BUCKET: ${S3_BUCKET}"
    inf "- S3_SECURE: ${S3_SECURE}"
    inf "- S3_EXTRACT_LOC: ${S3_EXTRACT_LOC}"
    inf "- S3_LOAD_LOC: ${S3_LOAD_LOC}"
    inf "- S3_REPORT_LOC: ${S3_REPORT_LOC}"
    inf "- S3_HISTORY_LOC: ${S3_HISTORY_LOC}"
    inf "- S3_BACKUP_LOC: ${S3_BACKUP_LOC}"
    echo ""
    good "Algorithm values:"
    inf "- ALGO_MODULE_PATH: ${ALGO_MODULE_PATH}"
    inf "- ALGO_NAME: ${ALGO_NAME}"
    inf "- ALGO_VERSION: ${ALGO_VERSION}"
    echo ""
    good "Backtest values:"
    inf "- NUM_DAYS_BACK: ${NUM_DAYS_BACK}"
    inf "- BACKTEST_START_DATE: ${BACKTEST_START_DATE}"
    inf "- BACKTEST_END_DATE:   ${BACKTEST_END_DATE}"
    echo ""
    good "Dataset name:"
    inf "- DATASET_NAME: ${DATASET_NAME}"
    echo ""
    date +"%Y-%m-%d %H:%m:%s"
    anmt "-------------------------------------"
}

show_s3_bucket_for_dataset() {
    uri=${1}
    use_bucket=$(echo ${uri} | sed -e 's|/| |g' | awk '{print $2}')
    test_local=$(echo ${s3_address} | grep localhost | wc -l)
    if [[ "${test_local}" == "0" ]]; then
        echo ""
        anmt "Checking AWS S3 bucket=${use_bucket} for dataset=${dataset_name} region=${S3_REGION_NAME}"
        echo "aws s3 ls s3://${use_bucket} | grep ${dataset_name}"
        aws s3 ls s3://${use_bucket} | grep ${dataset_name}
        echo ""
    else
        echo ""
        anmt "Checking Local S3 ${s3_address} bucket=${use_bucket} for dataset=${dataset_name}"
        echo "aws --endpoint-url http://${s3_address} s3 ls s3://${use_bucket} | grep ${dataset_name}"
        aws --endpoint-url http://${s3_address} s3 ls s3://${use_bucket} | grep ${dataset_name}
        echo ""
    fi
}

if [[ "${DEBUG_AE}" == "1" ]]; then
    show_algo_env
fi
