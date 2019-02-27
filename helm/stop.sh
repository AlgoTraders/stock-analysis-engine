#!/bin/bash

if [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
elif [[ -e ../analysis_engine/scripts/common_bash.sh ]]; then
    source ../analysis_engine/scripts/common_bash.sh
elif [[ -e ../../analysis_engine/scripts/common_bash.sh ]]; then
    source ../../analysis_engine/scripts/common_bash.sh
elif [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
fi

namespace="ae"

stop_all="0"
if [[ "${1}" == "-f" ]]; then
    stop_all="1"
fi

releases="ae ae-backup ae-intraday ae-daily ae-weekly ae-jupyter"
for r in ${releases}; do
    test_release=$(helm ls | grep ${r} | grep -v -E "ae-redis|ae-minio" | wc -l)
    if [[ "${test_release}" != "0" ]]; then
        anmt "deleting ${r} with helm"
        helm del --purge ${r}
    fi
done

if [[ "${stop_all}" == "1" ]]; then
    anmt "deleting ae-minio with helm"
    helm del --purge ae-minio
    anmt "deleting ae-redis with helm"
    helm del --purge ae-redis
fi

pods="engine backtester backup intraday daily weekly"
for p in ${pods}; do
    pod_name="${p}"
    not_done=$(/usr/bin/kubectl get po -n ${namespace} | grep ${pod_name} | wc -l)
    while [[ "${not_done}" != "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${pod_name} to stop"
        sleep 5
        /usr/bin/kubectl get po -n ${namespace} | grep ${pod_name}
        not_done=$(/usr/bin/kubectl get po -n ${namespace} | grep ${pod_name} | wc -l)
    done
done

anmt "removing secrets"
./_delete-secrets.sh
