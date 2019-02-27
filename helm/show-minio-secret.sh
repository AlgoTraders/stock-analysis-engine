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

anmt "------------------------------------"
anmt "getting ae-minio secret in ${namespace}: "

pod_name=$(kubectl -n ${namespace} get pod | grep ae-minio | grep -v Terminating | awk '{print $1}')
good "kubectl get secrets -n ${namespace} ${pod_name}"

kubectl get secrets -n ${namespace} ${pod_name} -o yaml
