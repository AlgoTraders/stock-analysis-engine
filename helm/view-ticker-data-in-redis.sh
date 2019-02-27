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

ticker="SPY"
namespace="ae"
pod_name=$(kubectl get pod -n ${namespace} | grep engine | grep -v Termin | head -1 | awk '{print $1}')

if [[ "${1}" != "" ]]; then
    ticker="${1}"
fi

anmt "------------------------------------"
anmt "ssh in ${namespace}: ${pod_name}"
good "kubectl -n ${namespace} ${pod_name} -- redis-cli -h ae-redis-master keys \"${ticker}_*\" | sort"

kubectl exec -it -n ${namespace} ${pod_name} -- redis-cli -h ae-redis-master keys "${ticker}_*" | sort
