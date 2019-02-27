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

use_namespace="ae"

anmt "---------------------------------------------------------"
anmt "Describing minio pod namespace ${use_namespace}"
inf ""
good "kubectl describe pod -n ${use_namespace} ae-redis-master-0"
inf ""
kubectl describe pod -n ${use_namespace} ae-redis-master-0
