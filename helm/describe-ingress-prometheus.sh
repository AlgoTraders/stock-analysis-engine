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
resource="ingress"
ing_name="ae-prometheus-server"

anmt "---------------------------------------------------------"
anmt "Describing prometheus ${resource} namespace ${namespace}"
inf ""
good "kubectl describe ${resource} -n ${namespace} ${ing_name}"
inf ""
kubectl describe ${resource} -n ${namespace} ${ing_name}
