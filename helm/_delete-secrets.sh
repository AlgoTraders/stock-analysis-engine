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

anmt "deleting secrets"
secrets=$(kubectl get secrets -n ${namespace} | grep "ae" | awk '{print $1}')
for s in ${secrets}; do
    anmt " - deleting secret ${s}"
    kubectl delete secret -n ${namespace} --ignore-not-found ${s}
done

exit 0
