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
resource="pod"

anmt "---------------------------------------------------------"
anmt "Describing engine ${resource} namespace ${namespace}"
inf ""
pod_name=$(kubectl get pod -n ${namespace} | grep engine | grep -v Termin | head -1 | awk '{print $1}')
good "kubectl describe ${resource} -n ${namespace} ${pod_name}"
inf ""
kubectl describe ${resource} -n ${namespace} ${pod_name}
