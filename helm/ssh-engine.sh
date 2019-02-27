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
pod_name=$(kubectl get pod -n ${namespace} | grep engine | grep -v Termin | head -1 | awk '{print $1}')

anmt "------------------------------------"
anmt "ssh in ${namespace}: ${pod_name}"
good "kubectl ${resource} -n ${namespace} ${pod_name} bash"

kubectl exec -it -n ${namespace} ${pod_name} bash
