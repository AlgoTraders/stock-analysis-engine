#!/bin/bash

job_name="intra"
repo=/opt/sa
log=/tmp/cron-ae.log

if [[ "${1}" != "" ]]; then
    job_name=${1}
fi
if [[ "${2}" != "" ]]; then
    export KUBECONFIG=${2}
else
    export KUBECONFIG=/opt/k8/config
fi
if [[ "${3}" != "" ]]; then
    repo=${3}
fi
if [[ "${4}" != "" ]]; then
    log=${4}
fi
if [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
fi

anmt "------------------------------------------------------" >> ${log}
anmt "starting ae job=${job_name} repo=${repo}" >> ${log}

pushd ${repo}/helm >> /dev/null
export PATH=${PATH}:/snap/bin

test_helm=$(which helm | wc -l)
if [[ "${test_helm}" == "0" ]]; then
    err "Please add helm to the cron job PATH env variable - helm not found" >> ${log}
    exit 1
fi

if [[ "${job_name}" == "intra" ]]; then
    ./run-intraday-job.sh -r >> ${log} 2>&1
elif [[ "${job_name}" == "daily" ]]; then
    ./run-daily-job.sh -r >> ${log} 2>&1
elif [[ "${job_name}" == "weekly" ]]; then
    ./run-weekly-job.sh -r >> ${log} 2>&1
elif [[ "${job_name}" == "backup" ]]; then
    ./run-backup-job.sh -r >> ${log} 2>&1
elif [[ "${job_name}" == "restore" ]]; then
    ./run-restore-job.sh -r >> ${log} 2>&1
else
    err "Unsupported job=${job_name} with repo=${repo}" >> ${log} 2>&1
fi
popd >> /dev/null

date -u +"%Y-%m-%d %H:%M:%S" >> ${log}
anmt "done" >> ${log}

exit
