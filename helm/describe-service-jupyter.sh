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
resource="service"

anmt "---------------------------------------------------------"
anmt "Describing jupyter ${resource} namespace ${namespace}"
inf ""
pod_name=$(kubectl get ${resource} -n ${namespace} | grep jupyter | grep -v Termin | head -1 | awk '{print $1}')
good "kubectl describe ${resource} -n ${namespace} ${pod_name}"
inf ""
kubectl describe ${resource} -n ${namespace} ${pod_name}
