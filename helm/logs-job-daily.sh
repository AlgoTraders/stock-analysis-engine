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
resource="log"

anmt "------------------------------------"
anmt "getting ${resource} in ${namespace}: "
pod_name=$(kubectl get pod -n ${namespace} | grep daily | grep -v Termin | head -1 | awk '{print $1}')
good "kubectl ${resource} -n ${namespace} ${pod_name}"

kubectl ${resource} -n ${namespace} ${pod_name}
